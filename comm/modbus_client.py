"""
Modbus Client - Modbus RTU/TCP haberleşme protokolü
"""
import socket
import struct
import time
from typing import Dict, Any, Optional, List
from datetime import datetime


class ModbusClient:
    """Modbus istemcisi"""
    
    def __init__(self, host: str, port: int = 502, unit_id: int = 1, 
                 timeout: int = 5, retry_count: int = 3):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.retry_count = retry_count
        self.connected = False
        self.socket = None
        self.transaction_id = 0
        
    def connect(self) -> bool:
        """Modbus sunucusuna bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Modbus connection error: {e}")
            return False
            
    def disconnect(self):
        """Bağlantıyı kes"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        
    def _create_modbus_request(self, function_code: int, start_address: int, 
                              count: int, data: bytes = b'') -> bytes:
        """Modbus isteği oluştur"""
        self.transaction_id += 1
        
        packet = bytearray()
        
        # MBAP Header
        packet.extend(struct.pack('>H', self.transaction_id))  # Transaction ID
        packet.extend(struct.pack('>H', 0))  # Protocol ID (0 for Modbus)
        packet.extend(struct.pack('>H', 6 + len(data)))  # Length
        packet.append(self.unit_id)  # Unit ID
        
        # Function Code
        packet.append(function_code)
        
        # Address and Count
        packet.extend(struct.pack('>H', start_address))
        packet.extend(struct.pack('>H', count))
        
        # Data (for write operations)
        if data:
            packet.extend(data)
            
        return bytes(packet)
        
    def _parse_modbus_response(self, response: bytes) -> Optional[bytes]:
        """Modbus yanıtını parse et"""
        if len(response) < 9:
            return None
            
        # MBAP Header kontrolü
        transaction_id = struct.unpack('>H', response[0:2])[0]
        protocol_id = struct.unpack('>H', response[2:4])[0]
        length = struct.unpack('>H', response[4:6])[0]
        unit_id = response[6]
        function_code = response[7]
        
        if transaction_id != self.transaction_id:
            return None
            
        if protocol_id != 0:
            return None
            
        if unit_id != self.unit_id:
            return None
            
        # Exception kontrolü
        if function_code & 0x80:
            exception_code = response[8]
            print(f"Modbus exception: {exception_code}")
            return None
            
        # Veri
        if len(response) > 8:
            return response[8:]
            
        return None
        
    def read_holding_registers(self, start_address: int, count: int) -> Optional[List[int]]:
        """Holding register'ları oku (Function Code 3)"""
        if not self.connected:
            if not self.connect():
                return None
                
        for attempt in range(self.retry_count):
            try:
                request = self._create_modbus_request(3, start_address, count)
                self.socket.send(request)
                
                response = self.socket.recv(1024)
                data = self._parse_modbus_response(response)
                
                if data and len(data) >= count * 2:
                    registers = []
                    for i in range(0, count * 2, 2):
                        register = struct.unpack('>H', data[i:i+2])[0]
                        registers.append(register)
                    return registers
                    
            except Exception as e:
                print(f"Read holding registers attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(0.1)
                    
        return None
        
    def read_input_registers(self, start_address: int, count: int) -> Optional[List[int]]:
        """Input register'ları oku (Function Code 4)"""
        if not self.connected:
            if not self.connect():
                return None
                
        for attempt in range(self.retry_count):
            try:
                request = self._create_modbus_request(4, start_address, count)
                self.socket.send(request)
                
                response = self.socket.recv(1024)
                data = self._parse_modbus_response(response)
                
                if data and len(data) >= count * 2:
                    registers = []
                    for i in range(0, count * 2, 2):
                        register = struct.unpack('>H', data[i:i+2])[0]
                        registers.append(register)
                    return registers
                    
            except Exception as e:
                print(f"Read input registers attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(0.1)
                    
        return None
        
    def read_coils(self, start_address: int, count: int) -> Optional[List[bool]]:
        """Coil'leri oku (Function Code 1)"""
        if not self.connected:
            if not self.connect():
                return None
                
        for attempt in range(self.retry_count):
            try:
                request = self._create_modbus_request(1, start_address, count)
                self.socket.send(request)
                
                response = self.socket.recv(1024)
                data = self._parse_modbus_response(response)
                
                if data and len(data) > 0:
                    coils = []
                    byte_count = data[0]
                    for i in range(1, byte_count + 1):
                        byte_value = data[i]
                        for bit in range(8):
                            if len(coils) < count:
                                coils.append(bool(byte_value & (1 << bit)))
                    return coils
                    
            except Exception as e:
                print(f"Read coils attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(0.1)
                    
        return None
        
    def read_discrete_inputs(self, start_address: int, count: int) -> Optional[List[bool]]:
        """Discrete input'ları oku (Function Code 2)"""
        if not self.connected:
            if not self.connect():
                return None
                
        for attempt in range(self.retry_count):
            try:
                request = self._create_modbus_request(2, start_address, count)
                self.socket.send(request)
                
                response = self.socket.recv(1024)
                data = self._parse_modbus_response(response)
                
                if data and len(data) > 0:
                    inputs = []
                    byte_count = data[0]
                    for i in range(1, byte_count + 1):
                        byte_value = data[i]
                        for bit in range(8):
                            if len(inputs) < count:
                                inputs.append(bool(byte_value & (1 << bit)))
                    return inputs
                    
            except Exception as e:
                print(f"Read discrete inputs attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(0.1)
                    
        return None
        
    def write_single_register(self, address: int, value: int) -> bool:
        """Tek register yaz (Function Code 6)"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            data = struct.pack('>H', value)
            request = self._create_modbus_request(6, address, 1, data)
            self.socket.send(request)
            
            response = self.socket.recv(1024)
            return self._parse_modbus_response(response) is not None
            
        except Exception as e:
            print(f"Write single register error: {e}")
            return False
            
    def write_multiple_registers(self, start_address: int, values: List[int]) -> bool:
        """Çoklu register yaz (Function Code 16)"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            data = bytearray()
            data.append(len(values) * 2)  # Byte count
            for value in values:
                data.extend(struct.pack('>H', value))
                
            request = self._create_modbus_request(16, start_address, len(values), data)
            self.socket.send(request)
            
            response = self.socket.recv(1024)
            return self._parse_modbus_response(response) is not None
            
        except Exception as e:
            print(f"Write multiple registers error: {e}")
            return False
            
    def read_diagnostics(self) -> Dict[str, Any]:
        """Teşhis verilerini oku"""
        if not self.connected:
            if not self.connect():
                return {"faults": [], "alarms": [], "error": "Connection failed"}
                
        try:
            faults = []
            alarms = []
            
            # Fault verilerini oku (Holding Register 1000-1099)
            fault_registers = self.read_holding_registers(1000, 100)
            if fault_registers:
                faults = self._parse_fault_registers(fault_registers)
                
            # Alarm verilerini oku (Holding Register 2000-2099)
            alarm_registers = self.read_holding_registers(2000, 100)
            if alarm_registers:
                alarms = self._parse_alarm_registers(alarm_registers)
                
            return {
                "faults": faults,
                "alarms": alarms,
                "timestamp": datetime.now().isoformat(),
                "source": f"Modbus:{self.host}:{self.port}"
            }
            
        except Exception as e:
            return {
                "faults": [],
                "alarms": [],
                "error": f"Read error: {str(e)}"
            }
            
    def _parse_fault_registers(self, registers: List[int]) -> List[Dict[str, Any]]:
        """Fault register'larını parse et"""
        faults = []
        
        for i in range(0, len(registers), 5):  # Her fault 5 register
            if i + 5 > len(registers):
                break
                
            fault_id = registers[i]
            component_id = registers[i + 1]
            severity = registers[i + 2]
            timestamp_high = registers[i + 3]
            timestamp_low = registers[i + 4]
            
            if fault_id > 0:  # Geçerli fault
                timestamp = (timestamp_high << 16) | timestamp_low
                
                fault = {
                    "id": f"F{fault_id:05d}",
                    "desc": f"Modbus Fault {fault_id}",
                    "component": self._get_component_name(component_id),
                    "severity": self._get_severity_name(severity),
                    "timestamp": datetime.fromtimestamp(timestamp).isoformat() if timestamp > 0 else None
                }
                faults.append(fault)
                
        return faults
        
    def _parse_alarm_registers(self, registers: List[int]) -> List[Dict[str, Any]]:
        """Alarm register'larını parse et"""
        alarms = []
        
        for i in range(0, len(registers), 4):  # Her alarm 4 register
            if i + 4 > len(registers):
                break
                
            alarm_id = registers[i]
            component_id = registers[i + 1]
            severity = registers[i + 2]
            status = registers[i + 3]
            
            if alarm_id > 0 and status > 0:  # Geçerli ve aktif alarm
                alarm = {
                    "id": f"A{alarm_id:05d}",
                    "desc": f"Modbus Alarm {alarm_id}",
                    "component": self._get_component_name(component_id),
                    "severity": self._get_severity_name(severity),
                    "status": "active" if status == 1 else "inactive",
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
        
    def _get_severity_name(self, severity: int) -> str:
        """Severity ID'den isim al"""
        severity_map = {
            1: "low",
            2: "medium", 
            3: "high",
            4: "critical"
        }
        return severity_map.get(severity, "unknown")
        
    def get_connection_status(self) -> Dict[str, Any]:
        """Bağlantı durumunu al"""
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "unit_id": self.unit_id,
            "timeout": self.timeout
        }
        
    def test_connection(self) -> bool:
        """Bağlantıyı test et"""
        if not self.connected:
            return self.connect()
            
        try:
            # Basit bir okuma işlemi ile test et
            test_data = self.read_holding_registers(0, 1)
            return test_data is not None
        except:
            return False
