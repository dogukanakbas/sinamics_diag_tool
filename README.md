# SINAMICS Diag & Viz (Enterprise Edition)

Bu gelişmiş sürüm; **CU320-2 PN** ile haberleşip arıza/alarmları okuyarak
bir **şema üstünde hatalı bloğu kırmızı** gösteren, genişletilebilir bir Python uygulamasıdır.

## 🚀 Yeni Özellikler (v3.0 - Enterprise)

### 🔐 **Güvenlik Sistemi**
- Kullanıcı kimlik doğrulama ve yetkilendirme
- Rol bazlı erişim kontrolü (Admin, Engineer, Operator)
- Şifreli konfigürasyon dosyaları
- Session yönetimi ve otomatik çıkış

### 🔌 **Gerçek Haberleşme Protokolleri**
- **PROFINET** - S7 PLC'ler ile haberleşme
- **Modbus TCP/RTU** - Endüstriyel cihazlarla haberleşme
- **EtherNet/IP** - Allen-Bradley cihazları ile haberleşme
- Otomatik bağlantı yönetimi ve hata toleransı

### 📊 **Gelişmiş Raporlama**
- **PDF Raporları** - Profesyonel teşhis raporları
- **Excel Raporları** - Detaylı analiz ve istatistikler
- **E-posta Entegrasyonu** - Otomatik rapor gönderimi
- **Grafik Analizler** - Trend analizi ve görselleştirme

### 🎯 **Mevcut Özellikler (v2.0)**
- **JSON Model Sistemi** - Farklı kart tipleri için esnek yapı
- **Command Adapter** - Harici teşhis araçları entegrasyonu
- **Gelişmiş UI** - Menü sistemi, model seçici, bağlantı durumu
- **Çoklu Veri Kaynağı** - Simulator, OPC UA, Command Adapter
- **Responsive Tasarım** - Dinamik boyutlandırma
- **Hata Yönetimi** - Güçlü hata yakalama ve kurtarma

## 📦 Kurulum

```bash
# Sanal ortam oluştur
python -m venv .venv

# Aktifleştir
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
python app.py
```

## 🏗️ Proje Yapısı

```
sinamics_diag_tool/
├── app.py                    # Ana uygulama
├── comm/                     # Haberleşme katmanı
│   ├── simulator.py         # Simülasyon veri kaynağı
│   ├── opcua_client.py      # OPC UA istemcisi
│   └── command_adapter.py   # Harici komut adaptörü
├── ui/
│   └── diagram.py           # Gelişmiş diyagram UI
├── diag/
│   ├── mapping.json         # Eski format (uyumluluk)
│   └── models/              # JSON model dosyaları
│       ├── sinamics_model.json
│       └── power_board_model.json
└── examples/
    └── test_adapter.py      # Örnek test adaptörü
```

## 🎮 Kullanım

### Temel Kullanım
```bash
# Varsayılan SINAMICS modeli ile simülatör
python app.py

# Özel model ile
python app.py --model diag/models/power_board_model.json

# Harici adaptör ile
python app.py --adapter "python examples/test_adapter.py"
```

### Klavye Kısayolları
- **A** - Alarm üret (Simulator modunda)
- **F** - Fault üret (Simulator modunda)
- **C** - Tümünü temizle (Simulator modunda)
- **F5** - Veriyi yenile
- **Ctrl+R** - Veriyi yenile

### Menü Özellikleri
- **File → Load Model** - Yeni model yükle
- **View → Model Info** - Model bilgilerini göster
- **View → Connection Status** - Bağlantı durumunu kontrol et
- **Help → Keyboard Shortcuts** - Kısayol listesi

## 🔌 Veri Kaynakları

### 1. Simulator (Varsayılan)
```python
# Klavye ile test
A - Alarm üret
F - Fault üret  
C - Temizle
```

### 2. OPC UA Client
```python
# S7-1500 köprüsü ile
from comm.opcua_client import OPCUAClient
client = OPCUAClient("opc.tcp://192.168.0.10:4840")
```

### 3. Command Adapter
```bash
# Harici komut çalıştır
python app.py --adapter "python my_diagnostic_script.py"
```

## 📋 JSON Model Formatı

```json
{
  "title": "SINAMICS CU320-2 PN Drive System",
  "components": [
    {
      "id": "inverter",
      "name": "Inverter", 
      "x": 470, "y": 240, "w": 160, "h": 110
    }
  ],
  "connections": [
    {"from": "dc_link", "to": "inverter"}
  ],
  "fault_map": {
    "F30012": "inverter"
  },
  "alarm_map": {
    "A05010": "fan"
  },
  "colors": {
    "normal": {"fill": "#1d1f23", "outline": "#5a5f6a"},
    "fault": {"fill": "#7f1d1d", "outline": "#ef4444"},
    "alarm": {"fill": "#1f2937", "outline": "#94a3b8"}
  }
}
```

## 🔧 Özel Adaptör Oluşturma

```python
#!/usr/bin/env python3
import json
import random

def main():
    # Teşhis verisi üret
    data = {
        "faults": [{"id": "F30012", "desc": "Overcurrent", "component": "inverter"}],
        "alarms": [{"id": "A05010", "desc": "Fan warning", "component": "fan"}]
    }
    
    # JSON olarak stdout'a yaz
    print(json.dumps(data))

if __name__ == "__main__":
    main()
```

## 🌐 OPC UA Köprüsü

Sahada tipik mimari:
```
SINAMICS CU320‑2 PN ←(PROFINET)→ S7‑1500 (OPC UA Server) ←OPC UA→ PC (bu uygulama)
```

OPC UA endpoint'i (`opc.tcp://<PLC_IP>:4840`) ve ilgili düğüm yollarını
`OPCUAClient` içinde düzenleyin.

## 🎯 Gelecek Özellikler

- [ ] Loglama sistemi
- [ ] Konfigürasyon dosyası
- [ ] Raporlama ve export
- [ ] Çoklu dil desteği
- [ ] Tema sistemi
- [ ] Grafik raporlama