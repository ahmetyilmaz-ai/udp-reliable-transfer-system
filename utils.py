import struct
import hashlib
import zlib

# Paket Başlığı (Header) Formatı:
# B: Unsigned Char (1 byte) -> Paket Tipi (0: Data, 1: ACK)
# I: Unsigned Int (4 byte) -> Sequence Numarası
# 16s: 16 Byte String -> MD5 Checksum (Bozulma kontrolü)
HEADER_FORMAT = 'B I 16s'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def calculate_checksum(payload):
    """Verinin MD5 özetini çıkarır (Bütünlük kontrolü için)."""
    return hashlib.md5(payload).digest()

def create_packet(pkt_type, seq_num, payload_str_or_bytes):
    """Veriyi alır, sıkıştırır, hash'ler ve UDP paketine çevirir."""
    if isinstance(payload_str_or_bytes, str):
        payload = payload_str_or_bytes.encode('utf-8')
    else:
        payload = payload_str_or_bytes

    # Bonus 1: Veriyi ağa çıkmadan önce sıkıştır (Hız kazandırır)
    compressed_payload = zlib.compress(payload)

    checksum = calculate_checksum(compressed_payload)
    header = struct.pack(HEADER_FORMAT, pkt_type, seq_num, checksum)
    return header + compressed_payload

def parse_packet(packet):
    """Gelen paketi parçalarına ayırır ve bozulma var mı diye bakar."""
    header = packet[:HEADER_SIZE]
    compressed_payload = packet[HEADER_SIZE:]

    pkt_type, seq_num, received_checksum = struct.unpack(HEADER_FORMAT, header)
    calculated_checksum = calculate_checksum(compressed_payload)

    # Checksum'lar eşleşmiyorsa yolda veri bozulmuş demektir
    is_corrupt = received_checksum != calculated_checksum

    # Sıkıştırmayı aç (Bozuksa boş döndür)
    try:
        payload = zlib.decompress(compressed_payload)
    except zlib.error:
        payload = b""

    return pkt_type, seq_num, is_corrupt, payload