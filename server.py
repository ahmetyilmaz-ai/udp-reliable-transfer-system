import socket
from utils import parse_packet, create_packet

LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 12345
BUFFER_SIZE = 4096

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    print(f"Sunucu başlatıldı. {LISTEN_IP}:{LISTEN_PORT} dinleniyor...")

    expected_seq = 0

    # Her çalıştığında eski dosyayı silip temiz bir tane açmasını sağlar
    with open("alinan_dosya.txt", "wb") as f:
        pass

    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        pkt_type, seq_num, is_corrupt, payload = parse_packet(data)

        if is_corrupt:
            print(f"Bozuk paket alındı (Seq: {seq_num}), reddedildi.")
            continue # Bozuksa cevap verme, istemci tekrar göndersin

        if pkt_type == 0: # Eğer gelen bir DATA (0) paketi ise
            # Doğru sıradaki paket mi geldi? (Kopya paketleri engelleme)
            if seq_num == expected_seq:
                with open("alinan_dosya.txt", "ab") as f:
                    f.write(payload)
                print(f"Paket kaydedildi: Seq {seq_num}")
                expected_seq += 1
            else:
                print(f"Kopya/Eski paket (Seq: {seq_num}), sadece ACK gönderiliyor.")

            # Her durumda istemciye "Aldım" (ACK) mesajı gönder
            ack_packet = create_packet(1, seq_num, b"ACK")
            server_socket.sendto(ack_packet, addr)

if __name__ == "__main__":
    start_server()