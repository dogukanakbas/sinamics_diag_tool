#!/usr/bin/env python3
"""
Test Adapter - Örnek teşhis adaptörü
Bu dosya, Command Adapter ile kullanılmak üzere tasarlanmıştır.
Stdout'a JSON formatında teşhis verisi yazar.

Kullanım:
python test_adapter.py
python app.py --adapter "python examples/test_adapter.py"
"""

import json
import random
import time
import sys

def generate_diagnostics():
    """Rastgele teşhis verisi üret"""
    # Rastgele durum seç
    r = random.choice([0, 1, 2, 3])
    
    if r == 0:
        # Fault durumu
        data = {
            "faults": [
                {"id": "F30012", "desc": "Overcurrent", "component": "inverter"}
            ],
            "alarms": []
        }
    elif r == 1:
        # Alarm durumu
        data = {
            "faults": [],
            "alarms": [
                {"id": "A05010", "desc": "Fan warning", "component": "fan"}
            ]
        }
    elif r == 2:
        # Hem fault hem alarm
        data = {
            "faults": [
                {"id": "F30005", "desc": "Rectifier fault", "component": "rectifier"}
            ],
            "alarms": [
                {"id": "A05020", "desc": "Temperature high", "component": "inverter"}
            ]
        }
    else:
        # Normal durum
        data = {
            "faults": [],
            "alarms": []
        }
    
    return data

def main():
    """Ana fonksiyon"""
    try:
        # Teşhis verisi üret
        diagnostics = generate_diagnostics()
        
        # JSON olarak stdout'a yaz
        print(json.dumps(diagnostics, indent=None))
        
    except Exception as e:
        # Hata durumunda boş veri döndür
        error_data = {
            "faults": [{"id": "ERROR", "desc": str(e), "component": "system"}],
            "alarms": []
        }
        print(json.dumps(error_data, indent=None))

if __name__ == "__main__":
    main()
