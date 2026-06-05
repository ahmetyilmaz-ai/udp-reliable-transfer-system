import socket
import time

def start_tcp_server(host='127.0.0.1', port=12346):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"TCP Sunucu {host}:{port} üzerinde dinliyor...")
        
        conn, addr = s.accept()
        with conn:
            print(f"Bağlantı kuruldu: {addr}")
            start_time = time.time()
            
            with open("tcp_received_file.bin", "wb") as f:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    
            elapsed = time.time() - start_time
            print(f"TCP ile dosya başarıyla alındı. Süre: {elapsed:.4f} saniye")

if __name__ == "__main__":
    start_tcp_server()