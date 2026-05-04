import socket
import time
import csv
import os
from utils import create_packet, parse_packet

DEST_IP = "127.0.0.1"
DEST_PORT = 12345
TIMEOUT = 2.0      # Cevap gelmezse 2 saniye bekle
MAX_RETRIES = 5    # Maksimum deneme sayısı
CHUNK_SIZE = 1024  # Dosyayı böleceğimiz parça boyutu (1 KB)

# Analiz için kullanacağı log listesi
event_logs = []

def log_event(event_type, seq_num, details=""):
    """Olayları zaman damgasıyla listeye ekler."""
    event_logs.append({
        "timestamp": time.time(),
        "event": event_type,
        "seq_num": seq_num,
        "details": details
    })

def send_file(file_path):
    if not os.path.exists(file_path):
        print(f"Hata: {file_path} bulunamadı! Lütfen bir test dosyası oluşturun.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    start_time = time.time()

    print(f"Aktarım başlıyor: {file_path}")

    with open(file_path, "rb") as f:
        seq_num = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break # Dosya bitti

            packet = create_packet(0, seq_num, chunk)
            attempts = 0
            success = False

            while attempts < MAX_RETRIES:
                try:
                    log_event("SEND", seq_num, f"Deneme {attempts + 1}")
                    client_socket.sendto(packet, (DEST_IP, DEST_PORT))

                    # ACK bekle
                    ack_data, _ = client_socket.recvfrom(2048)
                    pkt_type, ack_seq, is_corrupt, _ = parse_packet(ack_data)

                    if pkt_type == 1 and ack_seq == seq_num and not is_corrupt:
                        log_event("ACK_RECEIVED", seq_num)
                        print(f"Parça {seq_num} başarıyla iletildi.")
                        success = True
                        break

                except socket.timeout:
                    attempts += 1
                    log_event("TIMEOUT", seq_num, f"Tekrar {attempts}")
                    print(f"Zaman aşımı! Parça {seq_num} tekrar deneniyor...")

            if not success:
                log_event("TRANSFER_FAILED", seq_num)
                print(f"Kritik Hata: Parça {seq_num} iletilemedi. Aktarım durduruldu.")
                break

            seq_num += 1

    save_logs_to_csv()
    print(f"\nBitti! Toplam Süre: {time.time() - start_time:.2f} saniye")

def save_logs_to_csv():
    """Toplanan logları CSV formatında kaydeder."""
    if not event_logs: return
    keys = event_logs[0].keys()
    with open("transfer_logs.csv", "w", newline="") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(event_logs)
    print("Loglar 'transfer_logs.csv' olarak kaydedildi.")

if __name__ == "__main__":
    # Test yapabilmek için aynı klasöre 'test_dosyasi.txt' adında bir dosya oluşturduk
    send_file("test_dosyasi.txt")