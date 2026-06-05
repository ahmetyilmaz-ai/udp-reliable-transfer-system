import pandas as pd
import matplotlib.pyplot as plt
import os

LOG_FILE = "transfer_logs.csv"

def analyze_logs(chunk_size=1024):
    if not os.path.exists(LOG_FILE):
        print(f"Hata: {LOG_FILE} bulunamadı. Önce client.py'yi çalıştırın.")
        return

    # Pandas ile veriyi okuyoruz
    df = pd.read_csv(LOG_FILE)

    # Temel ağ olaylarını filtreliyoruz
    send_events = df[df["event"] == "SEND"]
    timeout_events = df[df["event"] == "TIMEOUT"]
    
    total_packets_sent = len(send_events)
    
    # ÇİFTE SAYIM DÜZELTİLDİ: Yapay düşmeler zaten Timeout'a sebep olduğu için sadece Timeout'ları sayıyoruz
    total_lost_packets = len(timeout_events)
    
    # Aktarım süresini buluyoruz
    complete_event = df[df["event"] == "TRANSFER_COMPLETE"]
    if not complete_event.empty:
        elapsed_str = complete_event.iloc[0]["details"]
        total_time = float(elapsed_str.split("=")[1].replace("s", ""))
    else:
        total_time = df["timestamp"].max() - df["timestamp"].min()

    # Orijinal dosya boyutunu tahmin etme (START ve END paketleri hariç)
    unique_seqs = send_events["seq_num"].nunique()
    data_packets_count = max(0, unique_seqs - 2) 
    file_size_bytes = data_packets_count * chunk_size

    # Teknik Raporda istenen metriklerin hesaplanması
    throughput = (total_packets_sent * chunk_size) / total_time if total_time > 0 else 0
    goodput = file_size_bytes / total_time if total_time > 0 else 0
    loss_rate = (total_lost_packets / total_packets_sent) * 100 if total_packets_sent > 0 else 0

    # GRAFİK ÇÖKME KORUMASI: Başarılı paket sayısının sıfırın altına düşmesini engelliyoruz
    basarili_paket = max(0, total_packets_sent - total_lost_packets)

    # Terminal Çıktısı
    print("-" * 40)
    print("AĞ PERFORMANS ANALİZİ")
    print("-" * 40)
    print(f"Toplam Aktarım Süresi : {total_time:.3f} saniye")
    print(f"Toplam Gönderilen Paket: {total_packets_sent}")
    print(f"Kaybolan/Düşen Paket  : {total_lost_packets}")
    print("-" * 40)
    print(f"Throughput        : {throughput:.2f} Byte/s")
    print(f"Goodput           : {goodput:.2f} Byte/s")
    print(f"Packet Loss Rate  : %{loss_rate:.2f}")
    print("-" * 40)

    # Matplotlib ile Görselleştirme
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 1. Grafik: Hız Karşılaştırması
    axes[0].bar(["Throughput", "Goodput"], [throughput, goodput], color=['#3498db', '#2ecc71'])
    axes[0].set_title("Bant Genişliği ve Faydalı Yük Hızı")
    axes[0].set_ylabel("Hız (Byte/s)")

    # 2. Grafik: Paket Durumu (Pasta Grafik)
    if total_packets_sent > 0:
        axes[1].pie([basarili_paket, total_lost_packets], 
                    labels=["Başarılı Ulaşan", "Kaybolan / Zaman Aşımı"], 
                    autopct='%1.1f%%', 
                    colors=['#2ecc71', '#e74c3c'], 
                    startangle=90)
        axes[1].set_title("Paket İletim Oranı")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_logs()