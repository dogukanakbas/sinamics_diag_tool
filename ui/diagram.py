import json, os, tkinter as tk
from typing import Dict, Any, Optional, List

class DriveDiagram(tk.Frame):
    def __init__(self, master, model_path: Optional[str] = None):
        super().__init__(master, bg="#0f0f11")
        self.canvas = tk.Canvas(self, bg="#0f0f11", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", lambda e: self.draw())
        
        # Model yükle
        self.model = self._load_model(model_path)
        self.current = {"faults": [], "alarms": []}
        
        # UI ayarları
        self.font_title = ("Segoe UI", 16, "bold")
        self.font_component = ("Segoe UI", 12, "bold")
        self.font_status = ("Segoe UI", 11, "bold")
        self.font_help = ("Segoe UI", 9)
        
    def _load_model(self, model_path: Optional[str]) -> Dict[str, Any]:
        """Model dosyasını yükle, yoksa varsayılan model kullan"""
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
                
        # Varsayılan model (eski mapping.json'dan uyumluluk için)
        mapping_path = os.path.join(os.path.dirname(__file__), "..", "diag", "mapping.json")
        if os.path.exists(mapping_path):
            try:
                with open(mapping_path, "r", encoding="utf-8") as f:
                    old_map = json.load(f)
                return self._convert_old_mapping(old_map)
            except Exception:
                pass
                
        # En son çare: hardcoded varsayılan model
        return self._get_default_model()
        
    def _convert_old_mapping(self, old_map: Dict[str, Any]) -> Dict[str, Any]:
        """Eski mapping.json formatını yeni model formatına çevir"""
        return {
            "title": "SINAMICS Drive System",
            "components": [
                {"id": "rectifier", "name": "Rectifier", "x": 50, "y": 240, "w": 160, "h": 110},
                {"id": "dc_link", "name": "DC Link", "x": 260, "y": 240, "w": 160, "h": 110},
                {"id": "inverter", "name": "Inverter", "x": 470, "y": 240, "w": 160, "h": 110},
                {"id": "motor", "name": "Motor", "x": 680, "y": 240, "w": 160, "h": 110},
                {"id": "fan", "name": "Fan", "x": 470, "y": 380, "w": 160, "h": 80},
                {"id": "cu320", "name": "CU320-2 PN", "x": 260, "y": 120, "w": 370, "h": 70}
            ],
            "connections": [
                {"from": "rectifier", "to": "dc_link"},
                {"from": "dc_link", "to": "inverter"},
                {"from": "inverter", "to": "motor"}
            ],
            "fault_map": old_map.get("fault_map", {}),
            "colors": {
                "normal": {"fill": "#1d1f23", "outline": "#5a5f6a"},
                "healthy": {"fill": "#166534", "outline": "#22c55e"},
                "fault": {"fill": "#7f1d1d", "outline": "#ef4444"},
                "alarm": {"fill": "#1f2937", "outline": "#94a3b8"},
                "background": "#0f0f11",
                "text": "#e5e7eb",
                "text_secondary": "#cbd5e1"
            }
        }
        
    def _get_default_model(self) -> Dict[str, Any]:
        """Varsayılan model döndür"""
        return {
            "title": "Generic Drive System",
            "components": [
                {"id": "rectifier", "name": "Rectifier", "x": 50, "y": 240, "w": 160, "h": 110},
                {"id": "dc_link", "name": "DC Link", "x": 260, "y": 240, "w": 160, "h": 110},
                {"id": "inverter", "name": "Inverter", "x": 470, "y": 240, "w": 160, "h": 110},
                {"id": "motor", "name": "Motor", "x": 680, "y": 240, "w": 160, "h": 110}
            ],
            "connections": [
                {"from": "rectifier", "to": "dc_link"},
                {"from": "dc_link", "to": "inverter"},
                {"from": "inverter", "to": "motor"}
            ],
            "fault_map": {},
            "colors": {
                "normal": {"fill": "#1d1f23", "outline": "#5a5f6a"},
                "healthy": {"fill": "#166534", "outline": "#22c55e"},
                "fault": {"fill": "#7f1d1d", "outline": "#ef4444"},
                "alarm": {"fill": "#1f2937", "outline": "#94a3b8"},
                "background": "#0f0f11",
                "text": "#e5e7eb",
                "text_secondary": "#cbd5e1"
            }
        }

    def update_status(self, diag):
        self.current = diag or {"faults":[], "alarms":[]}
        self.draw()

    def draw(self):
        """Diyagramı çiz"""
        w = self.winfo_width() or 1000
        h = self.winfo_height() or 600
        self.canvas.delete("all")
        
        # Başlık
        title = self.model.get("title", "Drive System")
        self.canvas.create_text(w//2, 24, text=title, fill=self.model["colors"]["text"], 
                                font=self.font_title)
        
        # Bağlantıları çiz
        self._draw_connections()
        
        # Bileşenleri çiz
        self._draw_components()
        
        # Durum metinlerini çiz
        self._draw_status_text(w, h)
        
    def _draw_connections(self):
        """Bileşenler arası bağlantıları çiz"""
        components = {c["id"]: c for c in self.model.get("components", [])}
        
        for connection in self.model.get("connections", []):
            from_comp = components.get(connection.get("from"))
            to_comp = components.get(connection.get("to"))
            
            if not from_comp or not to_comp:
                continue
                
            # Bağlantı noktalarını hesapla
            from_x = from_comp["x"] + from_comp["w"]
            from_y = from_comp["y"] + from_comp["h"] // 2
            to_x = to_comp["x"]
            to_y = to_comp["y"] + to_comp["h"] // 2
            
            # Bağlantı çizgisi
            self.canvas.create_line(
                from_x, from_y, to_x, to_y,
                width=3, arrow=tk.LAST, fill="#bfbfbf"
            )
            
    def _draw_components(self):
        """Bileşenleri çiz"""
        faulted_components = set(self._affected_components())
        alarmed_components = set(self._alarmed_components())
        healthy_components = set(self._healthy_components())
        
        for component in self.model.get("components", []):
            comp_id = component["id"]
            name = component.get("name", comp_id)
            x, y, w, h = component["x"], component["y"], component["w"], component["h"]
            
            # Renk belirleme
            colors = self.model["colors"]
            if comp_id in faulted_components:
                fill = colors["fault"]["fill"]
                outline = colors["fault"]["outline"]
                width = 4
            elif comp_id in alarmed_components:
                fill = colors["alarm"]["fill"]
                outline = colors["alarm"]["outline"]
                width = 3
            elif comp_id in healthy_components:
                fill = colors["healthy"]["fill"]
                outline = colors["healthy"]["outline"]
                width = 3
            else:
                fill = colors["normal"]["fill"]
                outline = colors["normal"]["outline"]
                width = 3
                
            # Bileşeni çiz
            self._draw_component_block(x, y, w, h, name, fill, outline, width)
            
    def _draw_component_block(self, x, y, w, h, name, fill, outline, width):
        """Tek bir bileşen bloğunu çiz"""
        # Ana dikdörtgen
        rect_id = self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=fill, outline=outline, width=width,
            activeoutline="#ffffff", activewidth=2  # Hover efekti
        )
        
        # Bileşen adı
        text_id = self.canvas.create_text(
            x + w // 2, y + h // 2,
            text=name, fill=self.model["colors"]["text"],
            font=self.font_component
        )
        
        # Component ID'yi bul
        comp_id = None
        for component in self.model.get("components", []):
            if (component["x"] == x and component["y"] == y and 
                component["w"] == w and component["h"] == h):
                comp_id = component["id"]
                break
        
        if comp_id:
            # Tıklanabilir alan için tag ekle
            self.canvas.addtag_withtag(f"component_{comp_id}", rect_id)
            self.canvas.addtag_withtag(f"component_{comp_id}", text_id)
            
            # Hover efekti için tag
            self.canvas.addtag_withtag("clickable", rect_id)
            self.canvas.addtag_withtag("clickable", text_id)
        
    def _draw_status_text(self, w, h):
        """Durum metinlerini çiz"""
        # Fault listesi
        fault_text = self._format_status_list(self.current.get("faults", []))
        self.canvas.create_text(
            20, h - 42, anchor="w",
            fill=self.model["colors"]["text"],
            font=self.font_status,
            text=f"Faults: {fault_text}"
        )
        
        # Alarm listesi
        alarm_text = self._format_status_list(self.current.get("alarms", []))
        self.canvas.create_text(
            20, h - 20, anchor="w",
            fill=self.model["colors"]["text_secondary"],
            font=self.font_status,
            text=f"Alarms: {alarm_text}"
        )
        
        # Yardım metni
        help_text = "A: Alarm  F: Fault  C: Clear  H: Healthy"
        self.canvas.create_text(
            w - 12, h - 12, anchor="se",
            fill="#9ca3af", font=self.font_help,
            text=help_text
        )
        
    def _format_status_list(self, items):
        """Durum listesini formatla"""
        if not items:
            return "—"
        return ", ".join(f"{item.get('id')}({item.get('component', '?')})" for item in items)

    def _affected_components(self):
        """Fault'lu bileşenleri döndür"""
        affected = []
        fault_map = self.model.get("fault_map", {})
        
        for fault in self.current.get("faults", []):
            comp = fault.get("component")
            if comp:
                affected.append(comp)
                continue
                
            # ID eşlemesi
            comp = fault_map.get(fault.get("id"))
            if comp:
                affected.append(comp)
                
        return affected
        
    def _alarmed_components(self):
        """Alarm'lı bileşenleri döndür"""
        affected = []
        alarm_map = self.model.get("alarm_map", {})
        
        for alarm in self.current.get("alarms", []):
            comp = alarm.get("component")
            if comp:
                affected.append(comp)
                continue
                
            # ID eşlemesi
            comp = alarm_map.get(alarm.get("id"))
            if comp:
                affected.append(comp)
                
        return affected
        
    def _healthy_components(self):
        """Sağlıklı bileşenleri döndür (healthy scenario aktifken)"""
        # Eğer healthy scenario aktifse tüm bileşenleri sağlıklı göster
        if hasattr(self, 'current') and self.current.get("healthy_scenario", False):
            return [comp["id"] for comp in self.model.get("components", [])]
        return []
        
    def load_model(self, model_path: str):
        """Yeni model yükle"""
        self.model = self._load_model(model_path)
        self.draw()
        
    def get_model_info(self):
        """Mevcut model bilgilerini döndür"""
        return {
            "title": self.model.get("title", "Unknown"),
            "components": len(self.model.get("components", [])),
            "connections": len(self.model.get("connections", [])),
            "fault_mappings": len(self.model.get("fault_map", {})),
            "alarm_mappings": len(self.model.get("alarm_map", {}))
        }
