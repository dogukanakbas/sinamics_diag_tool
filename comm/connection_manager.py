"""
Connection Manager - Gelişmiş bağlantı yönetimi
"""
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


class IConnectionManager(ABC):
    """Bağlantı yöneticisi arayüzü"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Bağlantı kur"""
        pass
        
    @abstractmethod
    def disconnect(self):
        """Bağlantıyı kes"""
        pass
        
    @abstractmethod
    def is_connected(self) -> bool:
        """Bağlantı durumu"""
        pass
        
    @abstractmethod
    def test_connection(self) -> bool:
        """Bağlantıyı test et"""
        pass
        
    @abstractmethod
    def read_diagnostics(self) -> Dict[str, Any]:
        """Teşhis verilerini oku"""
        pass


class ConnectionManager:
    """Gelişmiş bağlantı yöneticisi"""
    
    def __init__(self, connection: IConnectionManager, 
                 auto_reconnect: bool = True,
                 reconnect_interval: int = 30,
                 health_check_interval: int = 60):
        self.connection = connection
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.health_check_interval = health_check_interval
        
        self._connected = False
        self._last_health_check = None
        self._reconnect_thread = None
        self._health_check_thread = None
        self._running = False
        
        # Callback'ler
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        # İstatistikler
        self.stats = {
            'connection_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'last_connection_time': None,
            'last_error': None,
            'uptime': 0
        }
        
    def start(self):
        """Bağlantı yöneticisini başlat"""
        self._running = True
        
        # İlk bağlantıyı dene
        self._attempt_connection()
        
        # Health check thread'ini başlat
        if self.auto_reconnect:
            self._health_check_thread = threading.Thread(
                target=self._health_check_loop, daemon=True
            )
            self._health_check_thread.start()
            
    def stop(self):
        """Bağlantı yöneticisini durdur"""
        self._running = False
        
        # Thread'leri bekle
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            self._reconnect_thread.join(timeout=5)
            
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)
            
        # Bağlantıyı kes
        self.disconnect()
        
    def _attempt_connection(self):
        """Bağlantı denemesi yap"""
        self.stats['connection_attempts'] += 1
        
        try:
            if self.connection.connect():
                self._connected = True
                self.stats['successful_connections'] += 1
                self.stats['last_connection_time'] = datetime.now()
                
                if self.on_connect_callback:
                    self.on_connect_callback()
                    
                print(f"Connected to {self.connection.__class__.__name__}")
            else:
                self._connected = False
                self.stats['failed_connections'] += 1
                
                if self.on_error_callback:
                    self.on_error_callback("Connection failed")
                    
        except Exception as e:
            self._connected = False
            self.stats['failed_connections'] += 1
            self.stats['last_error'] = str(e)
            
            if self.on_error_callback:
                self.on_error_callback(str(e))
                
    def disconnect(self):
        """Bağlantıyı kes"""
        if self._connected:
            try:
                self.connection.disconnect()
                self._connected = False
                
                if self.on_disconnect_callback:
                    self.on_disconnect_callback()
                    
                print(f"Disconnected from {self.connection.__class__.__name__}")
            except Exception as e:
                print(f"Error during disconnect: {e}")
                
    def _health_check_loop(self):
        """Health check döngüsü"""
        while self._running:
            try:
                if self._connected:
                    # Bağlantıyı test et
                    if not self.connection.test_connection():
                        print("Health check failed, attempting reconnect...")
                        self._connected = False
                        self._start_reconnect()
                else:
                    # Bağlantı yoksa yeniden dene
                    self._start_reconnect()
                    
                self._last_health_check = datetime.now()
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                print(f"Health check error: {e}")
                time.sleep(self.health_check_interval)
                
    def _start_reconnect(self):
        """Yeniden bağlanma işlemini başlat"""
        if not self.auto_reconnect or not self._running:
            return
            
        # Eğer zaten reconnect thread'i çalışıyorsa bekle
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return
            
        self._reconnect_thread = threading.Thread(
            target=self._reconnect_loop, daemon=True
        )
        self._reconnect_thread.start()
        
    def _reconnect_loop(self):
        """Yeniden bağlanma döngüsü"""
        while not self._connected and self._running:
            try:
                print(f"Attempting to reconnect in {self.reconnect_interval} seconds...")
                time.sleep(self.reconnect_interval)
                
                if self._running:
                    self._attempt_connection()
                    
            except Exception as e:
                print(f"Reconnect error: {e}")
                
    def read_diagnostics(self) -> Dict[str, Any]:
        """Teşhis verilerini oku"""
        if not self._connected:
            # Bağlantı yoksa otomatik bağlanmayı dene
            if self.auto_reconnect:
                self._attempt_connection()
                
            if not self._connected:
                return {
                    "faults": [],
                    "alarms": [],
                    "error": "Not connected",
                    "connection_status": "disconnected"
                }
                
        try:
            # Bağlantı varsa veri oku
            result = self.connection.read_diagnostics()
            result["connection_status"] = "connected"
            result["last_update"] = datetime.now().isoformat()
            return result
            
        except Exception as e:
            # Hata durumunda bağlantıyı kes
            self._connected = False
            self.stats['last_error'] = str(e)
            
            if self.on_error_callback:
                self.on_error_callback(str(e))
                
            return {
                "faults": [],
                "alarms": [],
                "error": f"Read error: {str(e)}",
                "connection_status": "error"
            }
            
    def get_connection_status(self) -> Dict[str, Any]:
        """Detaylı bağlantı durumu"""
        return {
            "connected": self._connected,
            "auto_reconnect": self.auto_reconnect,
            "last_health_check": self._last_health_check.isoformat() if self._last_health_check else None,
            "stats": self.stats.copy(),
            "connection_info": self.connection.get_connection_status() if hasattr(self.connection, 'get_connection_status') else {}
        }
        
    def set_callbacks(self, on_connect: Optional[Callable] = None,
                     on_disconnect: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """Callback'leri ayarla"""
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect
        self.on_error_callback = on_error


class EnhancedProfinetClient(IConnectionManager):
    """Gelişmiş PROFINET istemcisi"""
    
    def __init__(self, plc_ip: str, rack: int = 0, slot: int = 1, **kwargs):
        from .profinet_client import ProfinetClient
        self.client = ProfinetClient(plc_ip, rack, slot, **kwargs)
        
    def connect(self) -> bool:
        return self.client.connect()
        
    def disconnect(self):
        self.client.disconnect()
        
    def is_connected(self) -> bool:
        return self.client.connected
        
    def test_connection(self) -> bool:
        return self.client.test_connection()
        
    def read_diagnostics(self) -> Dict[str, Any]:
        return self.client.read_diagnostics()
        
    def get_connection_status(self) -> Dict[str, Any]:
        return self.client.get_connection_status()


class EnhancedModbusClient(IConnectionManager):
    """Gelişmiş Modbus istemcisi"""
    
    def __init__(self, host: str, port: int = 502, unit_id: int = 1, **kwargs):
        from .modbus_client import ModbusClient
        self.client = ModbusClient(host, port, unit_id, **kwargs)
        
    def connect(self) -> bool:
        return self.client.connect()
        
    def disconnect(self):
        self.client.disconnect()
        
    def is_connected(self) -> bool:
        return self.client.connected
        
    def test_connection(self) -> bool:
        return self.client.test_connection()
        
    def read_diagnostics(self) -> Dict[str, Any]:
        return self.client.read_diagnostics()
        
    def get_connection_status(self) -> Dict[str, Any]:
        return self.client.get_connection_status()
