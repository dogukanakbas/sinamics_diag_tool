"""
Command Adapter - Harici komutlarla teşhis verisi alma
Bu sınıf, stdout'a JSON yazan harici komutları çalıştırır ve sonuçları döndürür.
"""
import json
import subprocess
import threading
import time
from typing import Dict, Any, Optional


class CommandAdapter:
    """
    Harici bir komutu periyodik çalıştırır; stdout JSON bekler.
    
    Örnek kullanım:
    adapter = CommandAdapter("python my_diagnostic_script.py")
    diag = adapter.read_diagnostics()
    """
    
    def __init__(self, command: str, timeout: int = 3, poll_interval: float = 0.5):
        """
        Args:
            command: Çalıştırılacak komut (örn: "python my_script.py")
            timeout: Komut timeout süresi (saniye)
            poll_interval: Komut çalıştırma aralığı (saniye)
        """
        self.command = command
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._last_result = {"faults": [], "alarms": []}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        
    def start(self):
        """Arka planda komut çalıştırmayı başlat"""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Arka planda komut çalıştırmayı durdur"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            
    def _poll_loop(self):
        """Arka planda sürekli komut çalıştır"""
        while self._running:
            try:
                result = self._execute_command()
                if result:
                    with self._lock:
                        self._last_result = result
            except Exception:
                pass  # Hata durumunda son geçerli değeri koru
                
            time.sleep(self.poll_interval)
            
    def _execute_command(self) -> Optional[Dict[str, Any]]:
        """Komutu çalıştır ve JSON sonucu döndür"""
        try:
            # Komutu çalıştır
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                return None
                
            # JSON parse et
            output = result.stdout.strip()
            if not output:
                return None
                
            data = json.loads(output)
            
            # Veri formatını kontrol et
            if not isinstance(data, dict):
                return None
                
            # Gerekli alanları kontrol et
            if "faults" not in data:
                data["faults"] = []
            if "alarms" not in data:
                data["alarms"] = []
                
            return data
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            return None
            
    def read_diagnostics(self) -> Dict[str, Any]:
        """
        Son teşhis verilerini döndür
        
        Returns:
            {"faults": [...], "alarms": [...]} formatında veri
        """
        with self._lock:
            return json.loads(json.dumps(self._last_result))  # Deep copy
            
    def test_connection(self) -> bool:
        """Komut bağlantısını test et"""
        try:
            result = self._execute_command()
            return result is not None
        except Exception:
            return False
            
    def get_last_error(self) -> Optional[str]:
        """Son hata mesajını döndür"""
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if result.returncode != 0:
                return result.stderr.strip()
        except Exception as e:
            return str(e)
        return None


class TestAdapter:
    """
    Test amaçlı basit adaptör - rastgele fault/alarm üretir
    """
    
    def __init__(self):
        self._faults = []
        self._alarms = []
        
    def inject_fault(self, fault_id: str = "F_TEST", component: str = "test_component"):
        """Test fault'u ekle"""
        self._faults = [{"id": fault_id, "desc": "Test fault", "component": component}]
        
    def inject_alarm(self, alarm_id: str = "A_TEST", component: str = "test_component"):
        """Test alarm'ı ekle"""
        self._alarms = [{"id": alarm_id, "desc": "Test alarm", "component": component}]
        
    def clear(self):
        """Tüm fault/alarm'ları temizle"""
        self._faults.clear()
        self._alarms.clear()
        
    def read_diagnostics(self) -> Dict[str, Any]:
        """Test verilerini döndür"""
        return {"faults": list(self._faults), "alarms": list(self._alarms)}
