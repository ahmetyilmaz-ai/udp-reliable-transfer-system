# NetProbe: Güvenilir UDP Dosya Aktarım ve Ağ Performans Analiz Platformu

NetProbe, standart UDP protokolünün bağlantısız ve güvenilmez yapısını uygulama katmanında çözerek, kayıpsız ve güvenilir dosya aktarımı sağlayan bir ağ mühendisliği projesidir. Sistem, temel dosya aktarımının ötesine geçerek ağ koşullarını simüle edebilen, çoklu istemci destekleyen ve performans analizleri sunan kapsamlı bir platform olarak tasarlanmıştır.

## Öne Çıkan Özellikler

* **Uygulama Katmanında Güvenilirlik:** "Stop-and-Wait" (Dur-ve-Bekle) akış kontrolü, otomatik zaman aşımı (timeout), yeniden gönderim (retransmission) ve mükerrer (duplicate) paket engelleme mekanizmaları.
* **Çoklu İstemci Desteği (Multi-Client):** `ThreadPoolExecutor` kullanılarak sunucunun aynı anda birden fazla istemciye asenkron olarak hizmet verebilmesi.
* **Veri Optimizasyonu ve Bütünlük:** Ağ trafiğini azaltmak için `zlib` veri sıkıştırması; paket başlıklarında MD5 ve uçtan uca dosya doğrulamasında SHA-256 hash kontrolleri.
* **Ağ Simülasyonu:** Uygulama katmanında çalışan yapay paket kayıp (loss rate) modülü ile zorlu ağ koşullarının simüle edilmesi.
* **TCP Karşılaştırması ve Analiz:** Üretilen ağ günlüklerinin (`transfer_logs.csv`) Pandas ve Matplotlib kullanılarak analiz edilmesi ve standart TCP soketleriyle karşılaştırmalı performans ölçümleri.

## Kullanım Talimatları

**1. Sunucuyu Başlatma:**
Sunucu tarafında portu dinlemeye başlamak için terminale şunu yazın:
```bash
python server.py
```

**2. İstemci Üzerinden Dosya Gönderme:**
Farklı bir terminal penceresinde istemciyi çalıştırarak test dosyasını sunucuya iletin:
```bash
python client.py
```
*(Not: İstemci içerisindeki `loss_rate` parametresini değiştirerek farklı ağ koşullarını test edebilirsiniz.)*

**3. Performans Analizi ve Grafikleme:**
Aktarım tamamlandıktan sonra oluşan `transfer_logs.csv` dosyasını analiz etmek ve RTT/Throughput grafiklerini çizdirmek için:
```bash
python analysis.py
```

## 👥Geliştirici Ekip ve Görev Dağılımı
**Pınar Nida Tunca:** Çoklu istemci (Multi-client) desteği, eş zamanlı paket işleme (ThreadPoolExecutor), Pandas/Matplotlib ile veri analizi ve GitHub yönetimi.

**Ahmet Yılmaz:** UDP soket altyapısı, güvenilirlik algoritmaları (ACK, Timeout, Retransmission), kopya paket kontrolü ve yapay paket kayıp modülünün geliştirilmesi.

**Selin Şentürk:** Paket mimarisi (Header), dosya parçalama (chunking), zlib sıkıştırması, SHA-256 bütünlük kontrolü ve TCP karşılaştırmalı deney altyapısı.
