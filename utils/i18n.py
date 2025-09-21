"""
Internationalization (i18n) System - Çoklu dil desteği
"""
import json
import os
from typing import Dict, Any, Optional


class I18nManager:
    """Çoklu dil yöneticisi"""
    
    def __init__(self, locale_dir: str = "locales", default_language: str = "tr"):
        self.locale_dir = locale_dir
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self._load_translations()
        
    def _load_translations(self):
        """Çevirileri yükle"""
        for language in ['tr', 'en']:
            locale_file = os.path.join(self.locale_dir, f"{language}.json")
            if os.path.exists(locale_file):
                try:
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[language] = json.load(f)
                except Exception as e:
                    print(f"Failed to load locale {language}: {e}")
                    
    def set_language(self, language: str):
        """Dil ayarla"""
        if language in self.translations:
            self.current_language = language
        else:
            print(f"Language {language} not available, using default")
            
    def get_language(self) -> str:
        """Mevcut dili al"""
        return self.current_language
        
    def get_available_languages(self) -> list:
        """Mevcut dilleri al"""
        return list(self.translations.keys())
        
    def t(self, key: str, **kwargs) -> str:
        """Çeviri al (translate)"""
        try:
            # Nokta notasyonu ile nested key'leri destekle
            keys = key.split('.')
            value = self.translations.get(self.current_language, {})
            
            for k in keys:
                value = value[k]
                
            # String formatı için kwargs kullan
            if isinstance(value, str) and kwargs:
                return value.format(**kwargs)
            return str(value)
            
        except (KeyError, TypeError):
            # Fallback: varsayılan dil
            try:
                keys = key.split('.')
                value = self.translations.get(self.default_language, {})
                
                for k in keys:
                    value = value[k]
                    
                if isinstance(value, str) and kwargs:
                    return value.format(**kwargs)
                return str(value)
                
            except (KeyError, TypeError):
                # Son çare: key'i döndür
                return key
                
    def get_menu_text(self, menu_key: str) -> str:
        """Menü metni al"""
        return self.t(f"menu.{menu_key}")
        
    def get_status_text(self, status_key: str) -> str:
        """Durum metni al"""
        return self.t(f"status.{status_key}")
        
    def get_component_name(self, component_key: str) -> str:
        """Bileşen adı al"""
        return self.t(f"components.{component_key}")
        
    def get_message(self, message_key: str, **kwargs) -> str:
        """Mesaj al"""
        return self.t(f"messages.{message_key}", **kwargs)
        
    def get_error_message(self, error_key: str, **kwargs) -> str:
        """Hata mesajı al"""
        return self.t(f"errors.{error_key}", **kwargs)
        
    def get_shortcut_text(self, shortcut_key: str) -> str:
        """Kısayol metni al"""
        return self.t(f"shortcuts.{shortcut_key}")
        
    def get_about_info(self) -> Dict[str, Any]:
        """Hakkında bilgilerini al"""
        return {
            'title': self.t('about.title'),
            'description': self.t('about.description'),
            'features': self.t('about.features')
        }
        
    def format_shortcuts(self) -> str:
        """Kısayolları formatla"""
        shortcuts = [
            self.get_shortcut_text('inject_alarm'),
            self.get_shortcut_text('inject_fault'),
            self.get_shortcut_text('clear_all'),
            self.get_shortcut_text('refresh_data'),
            self.get_shortcut_text('refresh_data_ctrl')
        ]
        
        return f"{self.get_shortcut_text('title')}:\n" + "\n".join(shortcuts)
        
    def get_app_title(self) -> str:
        """Uygulama başlığını al"""
        return self.t('app.title')
        
    def get_app_version(self) -> str:
        """Uygulama sürümünü al"""
        return self.t('app.version')


# Global i18n instance
i18n = I18nManager()
