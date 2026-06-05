import socket
import time
import sys
import os

def send_file_tcp(file_path, host='127.0.0.1', port=12346):
    if not os.path.exists(file_path):
        print(f"Hata: {file_path} bulunamadı!")
        return
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"{file_path} TCP üzerinden gönderiliyor...")
        
        start_time = time.time()
        with open(file_path, "rb") as f:
            s.sendall(f.read())
            
        elapsed = time.time() - start_time
        print(f"TCP Gönderimi tamamlandı. Süre: {elapsed:.4f} saniye")

if __name__ == "__main__":
    file_to_send = sys.argv[1] if len(sys.argv) > 1 else "test_dosyasi.txt"
    send_file_tcp(file_to_send)