"""
Configuration Management System
"""
import json
import os
from typing import Any, Dict, Optional


class ConfigManager:
    """Konfigürasyon yöneticisi"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Config load error: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon"""
        return {
            "app": {
                "title": "SINAMICS Diag & Viz (Enhanced)",
                "version": "2.0",
                "window_size": {"width": 1000, "height": 640},
                "poll_interval": 500,
                "auto_save": True
            },
            "ui": {
                "theme": "dark",
                "language": "tr",
                "show_help": True,
                "show_status_bar": True,
                "font_size": 12
            },
            "logging": {
                "enabled": True,
                "log_level": "INFO",
                "log_directory": "logs",
                "max_log_files": 30,
                "console_output": False
            },
            "models": {
                "default_model": "diag/models/sinamics_model.json",
                "recent_models": []
            },
            "adapters": {
                "default_adapter": "simulator",
                "opcua": {
                    "endpoint": "opc.tcp://192.168.0.10:4840",
                    "timeout": 5,
                    "retry_count": 3
                },
                "command": {
                    "timeout": 3,
                    "poll_interval": 0.5
                }
            },
            "history": {
                "enabled": True,
                "max_entries": 1000,
                "save_interval": 60
            },
            "export": {
                "default_format": "json",
                "include_timestamps": True,
                "include_metadata": True
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Konfigürasyon değeri al"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """Konfigürasyon değeri ayarla"""
        keys = key.split('.')
        config = self.config
        
        # Son anahtara kadar git
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Değeri ayarla
        config[keys[-1]] = value
        
    def save(self):
        """Konfigürasyonu kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Config save error: {e}")
            return False
            
    def add_recent_model(self, model_path: str):
        """Son kullanılan modele ekle"""
        recent = self.get('models.recent_models', [])
        if model_path in recent:
            recent.remove(model_path)
        recent.insert(0, model_path)
        
        # Maksimum 5 model tut
        recent = recent[:5]
        self.set('models.recent_models', recent)
        
    def get_recent_models(self) -> list:
        """Son kullanılan modelleri al"""
        return self.get('models.recent_models', [])
        
    def get_window_size(self) -> tuple:
        """Pencere boyutunu al"""
        size = self.get('app.window_size', {'width': 1000, 'height': 640})
        return (size['width'], size['height'])
        
    def set_window_size(self, width: int, height: int):
        """Pencere boyutunu ayarla"""
        self.set('app.window_size', {'width': width, 'height': height})
        
    def get_poll_interval(self) -> int:
        """Polling aralığını al"""
        return self.get('app.poll_interval', 500)
        
    def set_poll_interval(self, interval: int):
        """Polling aralığını ayarla"""
        self.set('app.poll_interval', interval)
        
    def get_theme(self) -> str:
        """Tema ayarını al"""
        return self.get('ui.theme', 'dark')
        
    def set_theme(self, theme: str):
        """Tema ayarını ayarla"""
        self.set('ui.theme', theme)
        
    def get_language(self) -> str:
        """Dil ayarını al"""
        return self.get('ui.language', 'tr')
        
    def set_language(self, language: str):
        """Dil ayarını ayarla"""
        self.set('ui.language', language)
        
    def is_logging_enabled(self) -> bool:
        """Loglama aktif mi?"""
        return self.get('logging.enabled', True)
        
    def get_log_level(self) -> str:
        """Log seviyesini al"""
        return self.get('logging.log_level', 'INFO')
        
    def is_history_enabled(self) -> bool:
        """Geçmiş aktif mi?"""
        return self.get('history.enabled', True)
        
    def get_max_history_entries(self) -> int:
        """Maksimum geçmiş kayıt sayısını al"""
        return self.get('history.max_entries', 1000)
        
    def get_default_model(self) -> str:
        """Varsayılan model dosyasını al"""
        return self.get('models.default_model', 'diag/models/sinamics_model.json')
        
    def set_default_model(self, model_path: str):
        """Varsayılan model dosyasını ayarla"""
        self.set('models.default_model', model_path)
        
    def get_opcua_config(self) -> dict:
        """OPC UA konfigürasyonunu al"""
        return self.get('adapters.opcua', {})
        
    def get_command_config(self) -> dict:
        """Command adapter konfigürasyonunu al"""
        return self.get('adapters.command', {})


# Global config instance
config = ConfigManager()
