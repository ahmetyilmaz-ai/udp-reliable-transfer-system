import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
BUFFER_SIZE = 1024

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = "Merhaba sunucu"

    client_socket.sendto(
        message.encode("utf-8"),
        (SERVER_IP, SERVER_PORT)
    )

    print("Mesaj sunucuya gönderildi")

    data, server_address = client_socket.recvfrom(BUFFER_SIZE)

    response = data.decode("utf-8")

    print(f"Sunucudan cevap geldi: {response}")

    client_socket.close()

if __name__ == "__main__":
    main()