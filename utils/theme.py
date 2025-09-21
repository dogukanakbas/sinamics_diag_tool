"""
Theme Management System - Tema yönetim sistemi
"""
import json
import os
from typing import Dict, Any, Optional


class ThemeManager:
    """Tema yöneticisi"""
    
    def __init__(self, theme_dir: str = "themes", default_theme: str = "dark"):
        self.theme_dir = theme_dir
        self.default_theme = default_theme
        self.current_theme = default_theme
        self.themes = {}
        self._load_themes()
        
    def _load_themes(self):
        """Temaları yükle"""
        if not os.path.exists(self.theme_dir):
            return
            
        for theme_file in os.listdir(self.theme_dir):
            if theme_file.endswith('.json'):
                theme_name = os.path.splitext(theme_file)[0]
                theme_path = os.path.join(self.theme_dir, theme_file)
                
                try:
                    with open(theme_path, 'r', encoding='utf-8') as f:
                        self.themes[theme_name] = json.load(f)
                except Exception as e:
                    print(f"Failed to load theme {theme_name}: {e}")
                    
    def set_theme(self, theme_name: str):
        """Tema ayarla"""
        if theme_name in self.themes:
            self.current_theme = theme_name
        else:
            print(f"Theme {theme_name} not available, using default")
            
    def get_theme(self) -> str:
        """Mevcut tema adını al"""
        return self.current_theme
        
    def get_available_themes(self) -> list:
        """Mevcut temaları al"""
        return list(self.themes.keys())
        
    def get_theme_info(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Tema bilgilerini al"""
        theme = theme_name or self.current_theme
        return self.themes.get(theme, {})
        
    def get_color(self, color_key: str, theme_name: Optional[str] = None) -> str:
        """Renk al"""
        theme = theme_name or self.current_theme
        theme_data = self.themes.get(theme, {})
        
        # Nokta notasyonu ile nested key'leri destekle
        keys = color_key.split('.')
        value = theme_data.get('colors', {})
        
        for k in keys:
            value = value.get(k, {})
            
        if isinstance(value, str):
            return value
        elif isinstance(value, dict) and 'fill' in value:
            return value['fill']
        else:
            # Fallback: varsayılan tema
            return self._get_fallback_color(color_key)
            
    def _get_fallback_color(self, color_key: str) -> str:
        """Fallback renk al"""
        fallback_colors = {
            'background': '#0f0f11',
            'text': '#e5e7eb',
            'text_secondary': '#cbd5e1',
            'border': '#5a5f6a',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'success': '#10b981'
        }
        return fallback_colors.get(color_key, '#000000')
        
    def get_component_colors(self, component_type: str, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Bileşen renklerini al"""
        theme = theme_name or self.current_theme
        theme_data = self.themes.get(theme, {})
        components = theme_data.get('components', {})
        
        component_colors = components.get(component_type, {})
        
        return {
            'fill': component_colors.get('fill', self._get_fallback_color('background')),
            'outline': component_colors.get('outline', self._get_fallback_color('border')),
            'text': component_colors.get('text', self._get_fallback_color('text'))
        }
        
    def get_ui_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """UI renklerini al"""
        theme = theme_name or self.current_theme
        theme_data = self.themes.get(theme, {})
        return theme_data.get('ui', {})
        
    def get_all_colors(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Tüm renkleri al"""
        theme = theme_name or self.current_theme
        theme_data = self.themes.get(theme, {})
        return theme_data.get('colors', {})
        
    def create_custom_theme(self, name: str, base_theme: str = "dark", custom_colors: Dict[str, str] = None):
        """Özel tema oluştur"""
        if base_theme not in self.themes:
            print(f"Base theme {base_theme} not found")
            return False
            
        # Base tema'yı kopyala
        custom_theme = json.loads(json.dumps(self.themes[base_theme]))
        custom_theme['name'] = name
        custom_theme['description'] = f"Custom theme based on {base_theme}"
        
        # Özel renkleri uygula
        if custom_colors:
            for color_key, color_value in custom_colors.items():
                keys = color_key.split('.')
                colors = custom_theme.get('colors', {})
                
                # Nested key'leri oluştur
                current = colors
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = color_value
                
        # Tema dosyasını kaydet
        theme_path = os.path.join(self.theme_dir, f"{name}.json")
        try:
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(custom_theme, f, indent=2, ensure_ascii=False)
            
            # Temaları yeniden yükle
            self._load_themes()
            return True
        except Exception as e:
            print(f"Failed to create custom theme: {e}")
            return False
            
    def delete_theme(self, theme_name: str) -> bool:
        """Tema sil"""
        if theme_name in ['dark', 'light']:
            print("Cannot delete default themes")
            return False
            
        theme_path = os.path.join(self.theme_dir, f"{theme_name}.json")
        try:
            if os.path.exists(theme_path):
                os.remove(theme_path)
                if theme_name in self.themes:
                    del self.themes[theme_name]
                return True
        except Exception as e:
            print(f"Failed to delete theme: {e}")
        return False
        
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """Tema dışa aktar"""
        if theme_name not in self.themes:
            return False
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes[theme_name], f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to export theme: {e}")
            return False
            
    def import_theme(self, file_path: str) -> bool:
        """Tema içe aktar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                
            theme_name = theme_data.get('name', 'imported_theme')
            theme_path = os.path.join(self.theme_dir, f"{theme_name}.json")
            
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
                
            # Temaları yeniden yükle
            self._load_themes()
            return True
        except Exception as e:
            print(f"Failed to import theme: {e}")
            return False


# Global theme instance
theme = ThemeManager()
