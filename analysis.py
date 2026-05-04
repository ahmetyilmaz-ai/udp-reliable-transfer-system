import pandas as pd
import matplotlib.pyplot as plt
import os

LOG_FILE = "transfer_logs.csv"


def analyze_logs():
    if not os.path.exists(LOG_FILE):
        print(f"Hata: {LOG_FILE} bulunamadı. Önce client.py'yi çalıştırarak log üretmelisiniz.")
        return

    # Pandas ile veriyi okuduk
    df = pd.read_csv(LOG_FILE)

    print("--- VERİ ANALİZİ ÖZETİ ---")
    print(f"Toplam Ağ Olayı: {len(df)}")

    # Kaç kere Timeout (Paket kaybı) yaşanmış bulalım
    timeout_count = len(df[df['event'] == 'TIMEOUT'])
    print(f"Toplam Timeout Sayısı: {timeout_count}")

    # Ekrana görsel grafik çizdirme
    send_events = df[df['event'] == 'SEND']
    retry_counts = send_events.groupby('seq_num').size()

    plt.figure(figsize=(10, 5))
    retry_counts.plot(kind='bar', color='coral', edgecolor='black')
    plt.title("Paket Başına Gönderim Denemesi Sayısı")
    plt.xlabel("Sequence (Paket) Numarası")
    plt.ylabel("Gönderim Sayısı (1 = Tek seferde gitti, >1 = Retransmission)")
    plt.tight_layout()

    print("Grafik oluşturuluyor...")
    plt.show()


if __name__ == "__main__":
    analyze_logs()