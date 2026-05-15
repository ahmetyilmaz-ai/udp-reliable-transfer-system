import hashlib
import json
import struct
import zlib


PKT_DATA = 0
PKT_ACK = 1
PKT_START = 2
PKT_END = 3

# Header:
# B   -> packet type
# I   -> sequence number
# I   -> total packet count for the current transfer
# 16s -> MD5 checksum of the compressed payload
HEADER_FORMAT = "!BII16s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def calculate_checksum(payload):
    return hashlib.md5(payload).digest()


def calculate_file_checksum(file_path, chunk_size=1024 * 1024):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def create_packet(pkt_type, seq_num, payload=b"", total_packets=0):
    if isinstance(payload, str):
        payload = payload.encode("utf-8")

    compressed_payload = zlib.compress(payload)
    checksum = calculate_checksum(compressed_payload)
    header = struct.pack(HEADER_FORMAT, pkt_type, seq_num, total_packets, checksum)
    return header + compressed_payload


def parse_packet(packet):
    if len(packet) < HEADER_SIZE:
        return None, None, 0, True, b""

    header = packet[:HEADER_SIZE]
    compressed_payload = packet[HEADER_SIZE:]
    pkt_type, seq_num, total_packets, received_checksum = struct.unpack(HEADER_FORMAT, header)
    is_corrupt = received_checksum != calculate_checksum(compressed_payload)

    if is_corrupt:
        return pkt_type, seq_num, total_packets, True, b""

    try:
        payload = zlib.decompress(compressed_payload)
    except zlib.error:
        return pkt_type, seq_num, total_packets, True, b""

    return pkt_type, seq_num, total_packets, False, payload


def encode_json(data):
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def decode_json(payload):
    return json.loads(payload.decode("utf-8"))
