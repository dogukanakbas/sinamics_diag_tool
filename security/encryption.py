"""
Data Encryption System - Veri şifreleme sistemi
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Union


class DataEncryption:
    """Veri şifreleme sınıfı"""
    
    def __init__(self, password: str = None):
        self.password = password or self._get_default_password()
        self.key = self._derive_key(self.password)
        self.cipher = Fernet(self.key)
        
    def _get_default_password(self) -> str:
        """Varsayılan şifre al"""
        # Gerçek uygulamada bu bir konfigürasyon dosyasından veya environment variable'dan gelmeli
        return "sinamics_diag_default_key_2024"
        
    def _derive_key(self, password: str) -> bytes:
        """Şifreden anahtar türet"""
        # Salt oluştur (gerçek uygulamada bu sabit olmamalı)
        salt = b'sinamics_diag_salt_2024'
        
        # PBKDF2 ile anahtar türet
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
        
    def encrypt_string(self, text: str) -> str:
        """String şifrele"""
        try:
            encrypted_data = self.cipher.encrypt(text.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return text
            
    def decrypt_string(self, encrypted_text: str) -> str:
        """String şifresini çöz"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return encrypted_text
            
    def encrypt_file(self, input_file: str, output_file: str = None) -> bool:
        """Dosya şifrele"""
        try:
            if not output_file:
                output_file = input_file + '.encrypted'
                
            with open(input_file, 'rb') as f:
                data = f.read()
                
            encrypted_data = self.cipher.encrypt(data)
            
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
                
            return True
        except Exception as e:
            print(f"File encryption error: {e}")
            return False
            
    def decrypt_file(self, input_file: str, output_file: str = None) -> bool:
        """Dosya şifresini çöz"""
        try:
            if not output_file:
                if input_file.endswith('.encrypted'):
                    output_file = input_file[:-10]  # .encrypted uzantısını kaldır
                else:
                    output_file = input_file + '.decrypted'
                    
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
                
            return True
        except Exception as e:
            print(f"File decryption error: {e}")
            return False
            
    def encrypt_dict(self, data: dict) -> str:
        """Dictionary şifrele"""
        import json
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt_string(json_str)
        
    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Dictionary şifresini çöz"""
        import json
        json_str = self.decrypt_string(encrypted_data)
        return json.loads(json_str)


class SecureConfig:
    """Güvenli konfigürasyon yöneticisi"""
    
    def __init__(self, config_file: str = "security/secure_config.json"):
        self.config_file = config_file
        self.encryption = DataEncryption()
        self.config_data = {}
        self._load_config()
        
    def _load_config(self):
        """Konfigürasyonu yükle"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read()
                    self.config_data = self.encryption.decrypt_dict(encrypted_data)
            except Exception as e:
                print(f"Error loading secure config: {e}")
                self.config_data = {}
                
    def _save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            encrypted_data = self.encryption.encrypt_dict(self.config_data)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving secure config: {e}")
            
    def get(self, key: str, default=None):
        """Konfigürasyon değeri al"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value):
        """Konfigürasyon değeri ayarla"""
        keys = key.split('.')
        config = self.config_data
        
        # Son anahtara kadar git
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Değeri ayarla
        config[keys[-1]] = value
        self._save_config()
        
    def get_database_credentials(self) -> dict:
        """Veritabanı kimlik bilgilerini al"""
        return {
            'host': self.get('database.host', 'localhost'),
            'port': self.get('database.port', 5432),
            'database': self.get('database.name', 'sinamics_diag'),
            'username': self.get('database.username', 'admin'),
            'password': self.get('database.password', 'password')
        }
        
    def set_database_credentials(self, host: str, port: int, database: str, 
                                username: str, password: str):
        """Veritabanı kimlik bilgilerini ayarla"""
        self.set('database.host', host)
        self.set('database.port', port)
        self.set('database.name', database)
        self.set('database.username', username)
        self.set('database.password', password)
        
    def get_communication_credentials(self) -> dict:
        """Haberleşme kimlik bilgilerini al"""
        return {
            'profinet': {
                'plc_ip': self.get('communication.profinet.plc_ip', '192.168.1.100'),
                'rack': self.get('communication.profinet.rack', 0),
                'slot': self.get('communication.profinet.slot', 1),
                'username': self.get('communication.profinet.username', ''),
                'password': self.get('communication.profinet.password', '')
            },
            'modbus': {
                'host': self.get('communication.modbus.host', '192.168.1.101'),
                'port': self.get('communication.modbus.port', 502),
                'unit_id': self.get('communication.modbus.unit_id', 1)
            }
        }


# Global encryption instance
data_encryption = DataEncryption()
secure_config = SecureConfig()
