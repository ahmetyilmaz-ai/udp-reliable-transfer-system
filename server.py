import hashlib
import os
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from utils import (
    PKT_ACK,
    PKT_DATA,
    PKT_END,
    PKT_START,
    create_packet,
    decode_json,
    parse_packet,
)


LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 12345
BUFFER_SIZE = 4096
OUTPUT_DIR = "received_files"
MAX_WORKERS = 8


@dataclass
class ClientSession:
    file_name: str
    file_size: int
    total_chunks: int
    expected_sha256: str
    output_path: str
    expected_seq: int = 1
    received_chunks: set = field(default_factory=set)
    completed: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)


sessions = {}
sessions_lock = threading.Lock()
send_lock = threading.Lock()


def safe_file_name(file_name):
    return os.path.basename(file_name) or "received_file.bin"


def session_path(addr, file_name):
    host, port = addr
    prefix = f"{host.replace('.', '_')}_{port}"
    return os.path.join(OUTPUT_DIR, f"{prefix}_{safe_file_name(file_name)}")


def send_ack(server_socket, addr, seq_num, message="ACK"):
    session = get_session(addr)
    total_packets = session.total_chunks if session else 0
    packet = create_packet(PKT_ACK, seq_num, message, total_packets)
    with send_lock:
        server_socket.sendto(packet, addr)


def get_or_create_session(addr, metadata):
    output_path = session_path(addr, metadata["file_name"])
    session = ClientSession(
        file_name=safe_file_name(metadata["file_name"]),
        file_size=int(metadata["file_size"]),
        total_chunks=int(metadata["total_chunks"]),
        expected_sha256=metadata["sha256"],
        output_path=output_path,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "wb"):
        pass

    with sessions_lock:
        sessions[addr] = session

    return session


def get_session(addr):
    with sessions_lock:
        return sessions.get(addr)


def remove_session(addr):
    with sessions_lock:
        sessions.pop(addr, None)


def verify_file(session):
    hasher = hashlib.sha256()
    total_size = 0

    with open(session.output_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            hasher.update(chunk)

    return total_size == session.file_size and hasher.hexdigest() == session.expected_sha256


def handle_start(server_socket, addr, seq_num, payload):
    try:
        metadata = decode_json(payload)
        session = get_or_create_session(addr, metadata)
        print(f"Transfer started from {addr}: {session.file_name}")
        send_ack(server_socket, addr, seq_num)
    except (KeyError, ValueError, OSError) as exc:
        print(f"Invalid START packet from {addr}: {exc}")
        send_ack(server_socket, addr, seq_num, "ERROR")


def handle_data(server_socket, addr, seq_num, payload):
    session = get_session(addr)
    if session is None:
        print(f"DATA without START from {addr}, seq={seq_num}")
        send_ack(server_socket, addr, seq_num, "NO_SESSION")
        return

    with session.lock:
        if seq_num in session.received_chunks:
            print(f"Duplicate packet ignored from {addr}: seq={seq_num}")
            send_ack(server_socket, addr, seq_num)
            return

        if seq_num != session.expected_seq:
            print(f"Out-of-order packet from {addr}: seq={seq_num}, expected={session.expected_seq}")
            send_ack(server_socket, addr, seq_num, "OUT_OF_ORDER")
            return

        with open(session.output_path, "ab") as file:
            file.write(payload)

        session.received_chunks.add(seq_num)
        session.expected_seq += 1
        print(f"Chunk written from {addr}: seq={seq_num}")
        send_ack(server_socket, addr, seq_num)


def handle_end(server_socket, addr, seq_num, payload):
    session = get_session(addr)
    if session is None:
        send_ack(server_socket, addr, seq_num, "NO_SESSION")
        return

    with session.lock:
        if session.completed:
            send_ack(server_socket, addr, seq_num, "OK")
            return

        expected_end_seq = session.total_chunks + 1
        if seq_num != expected_end_seq:
            send_ack(server_socket, addr, seq_num, "OUT_OF_ORDER")
            return

        is_complete = len(session.received_chunks) == session.total_chunks and verify_file(session)
        if is_complete:
            session.completed = True
            print(f"Transfer verified: {session.output_path}")
            send_ack(server_socket, addr, seq_num, "OK")
            remove_session(addr)
        else:
            print(f"Checksum or size mismatch for {addr}: {session.output_path}")
            send_ack(server_socket, addr, seq_num, "CHECKSUM_ERROR")


def process_packet(server_socket, data, addr):
    pkt_type, seq_num, total_packets, is_corrupt, payload = parse_packet(data)

    if is_corrupt:
        print(f"Corrupt packet ignored from {addr}, seq={seq_num}")
        return

    if pkt_type == PKT_START:
        handle_start(server_socket, addr, seq_num, payload)
    elif pkt_type == PKT_DATA:
        handle_data(server_socket, addr, seq_num, payload)
    elif pkt_type == PKT_END:
        handle_end(server_socket, addr, seq_num, payload)
    else:
        print(f"Unknown packet type from {addr}: type={pkt_type}, seq={seq_num}")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    print(f"Server listening on {LISTEN_IP}:{LISTEN_PORT}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            executor.submit(process_packet, server_socket, data, addr)


if __name__ == "__main__":
    start_server()
