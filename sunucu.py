import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
BUFFER_SIZE = 1024

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # AF_INET: IPv4, SOCK_DGRAM: UDP kullanılacağı anlamına gelir.

    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f"Sunucu başlatıldı: {SERVER_IP}:{SERVER_PORT}")
    print("Mesaj bekleniyor...")

    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)

        message = data.decode("utf-8")

        print(f"İstemciden mesaj geldi: {message}")
        print(f"İstemci adresi: {client_address}")

        response = "Mesaj alındı"
        server_socket.sendto(response.encode("utf-8"), client_address)

if __name__ == "__main__":
    main()