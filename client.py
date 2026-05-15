import argparse
import csv
import os
import socket
import time

from utils import (
    PKT_ACK,
    PKT_DATA,
    PKT_END,
    PKT_START,
    calculate_file_checksum,
    create_packet,
    encode_json,
    parse_packet,
)


DEST_IP = "127.0.0.1"
DEST_PORT = 12345
TIMEOUT = 2.0
MAX_RETRIES = 5
CHUNK_SIZE = 1024
LOG_FILE = "transfer_logs.csv"

event_logs = []


def log_event(event_type, seq_num, details=""):
    event_logs.append(
        {
            "timestamp": time.time(),
            "event": event_type,
            "seq_num": seq_num,
            "details": details,
        }
    )


def wait_for_ack(client_socket, expected_seq):
    while True:
        ack_data, _ = client_socket.recvfrom(4096)
        pkt_type, ack_seq, _total_packets, is_corrupt, payload = parse_packet(ack_data)

        if is_corrupt:
            log_event("CORRUPT_ACK", expected_seq)
            continue

        if pkt_type == PKT_ACK and ack_seq == expected_seq:
            return payload.decode("utf-8", errors="replace")

        log_event("UNEXPECTED_ACK", expected_seq, f"type={pkt_type}, seq={ack_seq}")


def send_with_retry(client_socket, packet, seq_num, description, expected_ack="ACK"):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_event("SEND", seq_num, f"{description}, attempt={attempt}")
            client_socket.sendto(packet, (DEST_IP, DEST_PORT))
            ack_payload = wait_for_ack(client_socket, seq_num)
            log_event("ACK_RECEIVED", seq_num, ack_payload)
            if ack_payload != expected_ack:
                raise RuntimeError(f"Unexpected ACK for {description} seq={seq_num}: {ack_payload}")
            return ack_payload
        except socket.timeout:
            log_event("TIMEOUT", seq_num, f"{description}, attempt={attempt}")
            print(f"Timeout: {description} seq={seq_num}, retry {attempt}/{MAX_RETRIES}")

    log_event("TRANSFER_FAILED", seq_num, description)
    raise TimeoutError(f"{description} seq={seq_num} could not be acknowledged")


def send_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    file_checksum = calculate_file_checksum(file_path)
    file_name = os.path.basename(file_path)

    metadata = {
        "file_name": file_name,
        "file_size": file_size,
        "chunk_size": CHUNK_SIZE,
        "total_chunks": total_chunks,
        "sha256": file_checksum,
    }

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    start_time = time.time()

    try:
        print(f"Transfer started: {file_name} ({file_size} bytes, {total_chunks} chunks)")

        start_packet = create_packet(PKT_START, 0, encode_json(metadata), total_chunks)
        send_with_retry(client_socket, start_packet, 0, "START")

        with open(file_path, "rb") as file:
            for seq_num in range(1, total_chunks + 1):
                chunk = file.read(CHUNK_SIZE)
                packet = create_packet(PKT_DATA, seq_num, chunk, total_chunks)
                send_with_retry(client_socket, packet, seq_num, "DATA")
                print(f"Chunk {seq_num}/{total_chunks} delivered")

        end_seq = total_chunks + 1
        end_packet = create_packet(PKT_END, end_seq, encode_json({"sha256": file_checksum}), total_chunks)
        send_with_retry(client_socket, end_packet, end_seq, "END", expected_ack="OK")

        elapsed = time.time() - start_time
        log_event("TRANSFER_COMPLETE", end_seq, f"elapsed={elapsed:.2f}s")
        print(f"Transfer complete in {elapsed:.2f} seconds")
    finally:
        client_socket.close()
        save_logs_to_csv()


def save_logs_to_csv():
    if not event_logs:
        return

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=event_logs[0].keys())
        writer.writeheader()
        writer.writerows(event_logs)
    print(f"Logs written to {LOG_FILE}")


def parse_args():
    parser = argparse.ArgumentParser(description="Reliable UDP file transfer client")
    parser.add_argument("file", nargs="?", default="test_dosyasi.txt", help="file to send")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    send_file(args.file)
