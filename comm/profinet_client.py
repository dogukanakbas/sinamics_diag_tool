"""
PROFINET Client - PROFINET haberleşme protokolü
"""
import socket
import struct
import time
from typing import Dict, Any, Optional, List
from datetime import datetime


class ProfinetClient:
    """PROFINET istemcisi"""
    
    def __init__(self, plc_ip: str, rack: int = 0, slot: int = 1, 
                 timeout: int = 5, retry_count: int = 3):
        self.plc_ip = plc_ip
        self.rack = rack
        self.slot = slot
        self.timeout = timeout
        self.retry_count = retry_count
        self.connected = False
        self.socket = None
        
        # PROFINET parametreleri
        self.port = 102  # ISO-TSAP port
        self.pdu_size = 240
        self.max_pdu_size = 240
        
    def connect(self) -> bool:
        """PLC'ye bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.plc_ip, self.port))
            
            # ISO bağlantısı kur
            if self._establish_iso_connection():
                self.connected = True
                return True
            else:
                self.disconnect()
                return False
                
        except Exception as e:
            print(f"PROFINET connection error: {e}")
            return False
            
    def _establish_iso_connection(self) -> bool:
        """ISO bağlantısı kur"""
        try:
            # ISO bağlantı paketi
            iso_packet = self._create_iso_connect_packet()
            self.socket.send(iso_packet)
            
            # Yanıt al
            response = self.socket.recv(1024)
            if len(response) > 0:
                return True
            return False
            
        except Exception as e:
            print(f"ISO connection error: {e}")
            return False
            
    def _create_iso_connect_packet(self) -> bytes:
        """ISO bağlantı paketi oluştur"""
        # Basitleştirilmiş ISO-TSAP paketi
        packet = bytearray()
        
        # ISO header
        packet.extend([0x03, 0x00, 0x00, 0x16])  # Length
        packet.extend([0x11, 0xE0])  # TPDU
        packet.extend([0x00, 0x00])  # Source TSAP
        packet.extend([0x00, 0x01])  # Destination TSAP
        packet.extend([0x00])  # Length
        
        return bytes(packet)
        
    def disconnect(self):
        """Bağlantıyı kes"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        
    def read_data(self, db_number: int, start_address: int, length: int) -> Optional[bytes]:
        """Veri oku"""
        if not self.connected:
            if not self.connect():
                return None
                
        for attempt in range(self.retry_count):
            try:
                # S7 read request paketi
                request = self._create_s7_read_request(db_number, start_address, length)
                self.socket.send(request)
                
                # Yanıt al
                response = self.socket.recv(1024)
                if len(response) > 0:
                    return self._parse_s7_response(response)
                    
            except Exception as e:
                print(f"Read attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(0.1)
                    
        return None
        
    def _create_s7_read_request(self, db_number: int, start_address: int, length: int) -> bytes:
        """S7 okuma isteği oluştur"""
        packet = bytearray()
        
        # ISO header
        packet.extend([0x03, 0x00, 0x00, 0x1F])  # Length
        packet.extend([0x02, 0xF0, 0x80])  # TPDU
        
        # S7 header
        packet.extend([0x32, 0x01, 0x00, 0x00])  # Protocol ID, Job ID
        packet.extend([0x00, 0x00, 0x08, 0x00])  # Parameters length, Data length
        packet.extend([0x00, 0x00])  # Error class, Error code
        
        # S7 parameter
        packet.extend([0x04, 0x01])  # Function, Item count
        packet.extend([0x12, 0x0A, 0x10])  # Item spec, Transport size, Length
        
        # Address
        if db_number > 0:
            packet.extend([0x05])  # DB type
            packet.extend(struct.pack('>H', db_number))  # DB number
        else:
            packet.extend([0x81])  # Input type
            
        packet.extend(struct.pack('>H', start_address))  # Start address
        packet.extend(struct.pack('>H', length))  # Length
        
        return bytes(packet)
        
    def _parse_s7_response(self, response: bytes) -> Optional[bytes]:
        """S7 yanıtını parse et"""
        if len(response) < 14:
            return None
            
        # Hata kontrolü
        error_class = response[17]
        error_code = response[18]
        
        if error_class != 0 or error_code != 0:
            print(f"S7 error: class={error_class}, code={error_code}")
            return None
            
        # Veri uzunluğu
        data_length = struct.unpack('>H', response[11:13])[0]
        
        if len(response) < 25 + data_length:
            return None
            
        # Veri
        return response[25:25 + data_length]
        
    def read_diagnostics(self) -> Dict[str, Any]:
        """Teşhis verilerini oku"""
        if not self.connected:
            if not self.connect():
                return {"faults": [], "alarms": [], "error": "Connection failed"}
                
        try:
            # Örnek: DB1'den fault/alarm verilerini oku
            # Gerçek uygulamada bu adresler PLC konfigürasyonuna göre ayarlanmalı
            fault_data = self.read_data(1, 0, 100)  # DB1, 0-99 byte
            alarm_data = self.read_data(1, 100, 100)  # DB1, 100-199 byte
            
            faults = []
            alarms = []
            
            if fault_data:
                faults = self._parse_fault_data(fault_data)
                
            if alarm_data:
                alarms = self._parse_alarm_data(alarm_data)
                
            return {
                "faults": faults,
                "alarms": alarms,
                "timestamp": datetime.now().isoformat(),
                "source": f"PROFINET:{self.plc_ip}"
            }
            
        except Exception as e:
            return {
                "faults": [],
                "alarms": [],
                "error": f"Read error: {str(e)}"
            }
            
    def _parse_fault_data(self, data: bytes) -> List[Dict[str, Any]]:
        """Fault verilerini parse et"""
        faults = []
        
        # Basit fault parsing (gerçek uygulamada daha karmaşık olacak)
        for i in range(0, len(data), 20):  # Her fault 20 byte
            if i + 20 > len(data):
                break
                
            fault_bytes = data[i:i+20]
            
            # Fault ID (ilk 4 byte)
            fault_id = struct.unpack('>I', fault_bytes[0:4])[0]
            
            if fault_id > 0:  # Geçerli fault
                # Component (byte 4-8)
                component_id = struct.unpack('>I', fault_bytes[4:8])[0]
                
                # Timestamp (byte 8-12)
                timestamp = struct.unpack('>I', fault_bytes[8:12])[0]
                
                fault = {
                    "id": f"F{fault_id:05d}",
                    "desc": f"PROFINET Fault {fault_id}",
                    "component": self._get_component_name(component_id),
                    "timestamp": datetime.fromtimestamp(timestamp).isoformat() if timestamp > 0 else None
                }
                faults.append(fault)
                
        return faults
        
    def _parse_alarm_data(self, data: bytes) -> List[Dict[str, Any]]:
        """Alarm verilerini parse et"""
        alarms = []
        
        # Basit alarm parsing
        for i in range(0, len(data), 16):  # Her alarm 16 byte
            if i + 16 > len(data):
                break
                
            alarm_bytes = data[i:i+16]
            
            # Alarm ID (ilk 4 byte)
            alarm_id = struct.unpack('>I', alarm_bytes[0:4])[0]
            
            if alarm_id > 0:  # Geçerli alarm
                # Component (byte 4-8)
                component_id = struct.unpack('>I', alarm_bytes[4:8])[0]
                
                alarm = {
                    "id": f"A{alarm_id:05d}",
                    "desc": f"PROFINET Alarm {alarm_id}",
                    "component": self._get_component_name(component_id),
                    "timestamp": datetime.now().isoformat()
                }
                alarms.append(alarm)
                
        return alarms
        
    def _get_component_name(self, component_id: int) -> str:
        """Component ID'den isim al"""
        component_map = {
            1: "inverter",
            2: "motor", 
            3: "rectifier",
            4: "dc_link",
            5: "fan",
            6: "cu320"
        }
        return component_map.get(component_id, f"component_{component_id}")
        
    def write_data(self, db_number: int, start_address: int, data: bytes) -> bool:
        """Veri yaz"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            # S7 write request paketi
            request = self._create_s7_write_request(db_number, start_address, data)
            self.socket.send(request)
            
            # Yanıt al
            response = self.socket.recv(1024)
            if len(response) > 0:
                return self._check_write_response(response)
                
        except Exception as e:
            print(f"Write error: {e}")
            
        return False
        
    def _create_s7_write_request(self, db_number: int, start_address: int, data: bytes) -> bytes:
        """S7 yazma isteği oluştur"""
        packet = bytearray()
        
        # ISO header
        packet.extend([0x03, 0x00, 0x00, 0x1F + len(data)])  # Length
        packet.extend([0x02, 0xF0, 0x80])  # TPDU
        
        # S7 header
        packet.extend([0x32, 0x01, 0x00, 0x00])  # Protocol ID, Job ID
        packet.extend(struct.pack('>H', 0x0E))  # Parameters length
        packet.extend(struct.pack('>H', len(data)))  # Data length
        packet.extend([0x00, 0x00])  # Error class, Error code
        
        # S7 parameter
        packet.extend([0x05, 0x01])  # Function, Item count
        packet.extend([0x12, 0x0A, 0x10])  # Item spec, Transport size, Length
        
        # Address
        if db_number > 0:
            packet.extend([0x05])  # DB type
            packet.extend(struct.pack('>H', db_number))  # DB number
        else:
            packet.extend([0x81])  # Input type
            
        packet.extend(struct.pack('>H', start_address))  # Start address
        packet.extend(struct.pack('>H', len(data)))  # Length
        
        # Data
        packet.extend(data)
        
        return bytes(packet)
        
    def _check_write_response(self, response: bytes) -> bool:
        """Yazma yanıtını kontrol et"""
        if len(response) < 14:
            return False
            
        # Hata kontrolü
        error_class = response[17]
        error_code = response[18]
        
        return error_class == 0 and error_code == 0
        
    def get_connection_status(self) -> Dict[str, Any]:
        """Bağlantı durumunu al"""
        return {
            "connected": self.connected,
            "plc_ip": self.plc_ip,
            "rack": self.rack,
            "slot": self.slot,
            "port": self.port,
            "timeout": self.timeout
        }
        
    def test_connection(self) -> bool:
        """Bağlantıyı test et"""
        if not self.connected:
            return self.connect()
            
        try:
            # Basit bir okuma işlemi ile test et
            test_data = self.read_data(1, 0, 4)
            return test_data is not None
        except:
            return False
