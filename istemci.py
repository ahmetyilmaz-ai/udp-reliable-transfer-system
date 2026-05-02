import json
import socket
import os

CHUNK_SIZE = 1024
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
TIMEOUT = 1.0
MAX_RETRIES = 5
def split_file(file_path, chunk_size=CHUNK_SIZE):
    chunks = []
    with open(file_path, "rb") as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            chunks.append(data)
    return chunks

def main():
    file_path = input("gönderilecek dosya yolu")
    if not os.path.exists(file_path):
        print("dosya bulunamadı")
        return
    chunks = split_file(file_path)

    print("dosya okundu", file_path)
    print("toplam dosya sayısı", len(chunks))
    print("parça boyutu", CHUNK_SIZE)

if __name__ == "__main__":
    main()