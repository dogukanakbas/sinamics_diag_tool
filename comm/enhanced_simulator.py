"""
Enhanced Simulator - Gelişmiş simülasyon sistemi
Gerçekçi component durumları ve dinamik senaryolar
"""
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading


class ComponentState:
    """Bileşen durumu"""
    
    def __init__(self, component_id: str, component_name: str):
        self.component_id = component_id
        self.component_name = component_name
        
        # Sağlık metrikleri
        self.health_score = 100.0  # 0-100 arası
        self.temperature = 25.0    # °C
        self.vibration = 0.0       # mm/s
        self.current = 0.0         # A
        self.voltage = 0.0         # V
        self.power = 0.0           # W
        
        # Durum değişkenleri
        self.is_running = False
        self.load_percentage = 0.0
        self.efficiency = 100.0
        
        # Arıza durumu
        self.faults = []
        self.alarms = []
        self.maintenance_due = False
        self.last_maintenance = datetime.now()
        
        # Trend verileri
        self.temperature_history = []
        self.vibration_history = []
        self.health_history = []
        
    def update_metrics(self, delta_time: float):
        """Metrikleri güncelle"""
        # Sıcaklık simülasyonu
        if self.is_running:
            # Yük bazlı sıcaklık artışı
            temp_increase = (self.load_percentage / 100.0) * 2.0
            # Rastgele varyasyon
            temp_variation = random.uniform(-0.5, 0.5)
            self.temperature += (temp_increase + temp_variation) * delta_time
            
            # Maksimum sıcaklık kontrolü
            max_temp = 80.0 + (self.health_score / 100.0) * 20.0
            self.temperature = min(self.temperature, max_temp)
        else:
            # Soğuma
            self.temperature -= 1.0 * delta_time
            self.temperature = max(self.temperature, 25.0)
            
        # Titreşim simülasyonu
        if self.is_running:
            base_vibration = (self.load_percentage / 100.0) * 5.0
            health_factor = (100.0 - self.health_score) / 100.0
            self.vibration = base_vibration + (health_factor * 10.0) + random.uniform(-0.5, 0.5)
        else:
            self.vibration = 0.0
            
        # Sağlık skoru hesaplama
        self._calculate_health_score()
        
        # Geçmiş verilerini güncelle
        self._update_history()
        
    def _calculate_health_score(self):
        """Sağlık skorunu hesapla"""
        # Sıcaklık etkisi
        temp_factor = 1.0
        if self.temperature > 60:
            temp_factor = max(0.0, 1.0 - (self.temperature - 60) / 40.0)
            
        # Titreşim etkisi
        vib_factor = 1.0
        if self.vibration > 5.0:
            vib_factor = max(0.0, 1.0 - (self.vibration - 5.0) / 15.0)
            
        # Yük etkisi
        load_factor = 1.0
        if self.load_percentage > 80:
            load_factor = max(0.0, 1.0 - (self.load_percentage - 80) / 20.0)
            
        # Sağlık skorunu güncelle
        health_change = (temp_factor + vib_factor + load_factor) / 3.0 - 1.0
        self.health_score += health_change * 0.1  # Yavaş değişim
        self.health_score = max(0.0, min(100.0, self.health_score))
        
    def _update_history(self):
        """Geçmiş verilerini güncelle"""
        current_time = datetime.now()
        
        # Son 100 veriyi sakla
        self.temperature_history.append((current_time, self.temperature))
        self.vibration_history.append((current_time, self.vibration))
        self.health_history.append((current_time, self.health_score))
        
        # Eski verileri temizle
        cutoff_time = current_time - timedelta(minutes=10)
        self.temperature_history = [(t, v) for t, v in self.temperature_history if t > cutoff_time]
        self.vibration_history = [(t, v) for t, v in self.vibration_history if t > cutoff_time]
        self.health_history = [(t, v) for t, v in self.health_history if t > cutoff_time]
        
    def get_status(self) -> Dict[str, Any]:
        """Bileşen durumunu al"""
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "health_score": round(self.health_score, 1),
            "temperature": round(self.temperature, 1),
            "vibration": round(self.vibration, 2),
            "current": round(self.current, 2),
            "voltage": round(self.voltage, 1),
            "power": round(self.power, 1),
            "is_running": self.is_running,
            "load_percentage": round(self.load_percentage, 1),
            "efficiency": round(self.efficiency, 1),
            "faults": len(self.faults),
            "alarms": len(self.alarms),
            "maintenance_due": self.maintenance_due,
            "days_since_maintenance": (datetime.now() - self.last_maintenance).days
        }


class EnhancedSimulator:
    """Gelişmiş simülatör - gerçekçi component durumları"""
    
    def __init__(self):
        self.components = {}
        self._running = False
        self._thread = None
        self._last_update = datetime.now()
        
        # Senaryo yönetimi
        self._current_scenario = None
        self._scenario_start_time = None
        
        # Bileşenleri oluştur
        self._initialize_components()
        
        # Fault/Alarm veritabanları
        self._setup_fault_alarm_database()
        
    def _initialize_components(self):
        """Bileşenleri başlat"""
        component_configs = [
            {"id": "rectifier", "name": "Rectifier"},
            {"id": "dc_link", "name": "DC Link"},
            {"id": "inverter", "name": "Inverter"},
            {"id": "motor", "name": "Motor"},
            {"id": "fan", "name": "Fan"},
            {"id": "cu320", "name": "CU320-2 PN"}
        ]
        
        for config in component_configs:
            self.components[config["id"]] = ComponentState(
                config["id"], config["name"]
            )
            
    def _setup_fault_alarm_database(self):
        """Fault/Alarm veritabanını kur"""
        self.fault_database = {
            "F30001": {"desc": "Motor overcurrent", "component": "motor", "severity": "high", "threshold": 50.0},
            "F30002": {"desc": "Motor overtemperature", "component": "motor", "severity": "high", "threshold": 75.0},
            "F30005": {"desc": "Rectifier overcurrent", "component": "rectifier", "severity": "high", "threshold": 45.0},
            "F30011": {"desc": "Motor bearing fault", "component": "motor", "severity": "medium", "threshold": 30.0},
            "F30012": {"desc": "Inverter overcurrent", "component": "inverter", "severity": "high", "threshold": 40.0},
            "F30020": {"desc": "DC link overvoltage", "component": "dc_link", "severity": "high", "threshold": 800.0},
            "F30021": {"desc": "DC link undervoltage", "component": "dc_link", "severity": "medium", "threshold": 400.0},
            "F30030": {"desc": "Fan failure", "component": "fan", "severity": "medium", "threshold": 20.0},
            "F30040": {"desc": "Control unit fault", "component": "cu320", "severity": "high", "threshold": 25.0},
            "F30050": {"desc": "Communication fault", "component": "cu320", "severity": "medium", "threshold": 15.0},
        }
        
        self.alarm_database = {
            "A05010": {"desc": "Fan speed low", "component": "fan", "severity": "low", "threshold": 10.0},
            "A05020": {"desc": "Motor temperature high", "component": "motor", "severity": "medium", "threshold": 65.0},
            "A05030": {"desc": "DC link voltage high", "component": "dc_link", "severity": "medium", "threshold": 750.0},
            "A05040": {"desc": "Inverter temperature high", "component": "inverter", "severity": "medium", "threshold": 70.0},
            "A05050": {"desc": "Communication warning", "component": "cu320", "severity": "low", "threshold": 5.0},
            "A05060": {"desc": "Motor bearing wear", "component": "motor", "severity": "low", "threshold": 8.0},
        }
        
    def start(self):
        """Simülatörü başlat"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self._thread.start()
            print("Enhanced Simulator started")
            
    def stop(self):
        """Simülatörü durdur"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("Enhanced Simulator stopped")
        
    def _simulation_loop(self):
        """Ana simülasyon döngüsü"""
        while self._running:
            try:
                current_time = datetime.now()
                delta_time = (current_time - self._last_update).total_seconds()
                self._last_update = current_time
                
                # Bileşenleri güncelle
                self._update_components(delta_time)
                
                # Fault/Alarm kontrolü
                self._check_faults_alarms()
                
                # Senaryo işleme
                if self._current_scenario:
                    self._process_scenario()
                    
                time.sleep(0.1)  # 100ms güncelleme
                
            except Exception as e:
                print(f"Simulation loop error: {e}")
                time.sleep(1.0)
                
    def _update_components(self, delta_time: float):
        """Bileşenleri güncelle"""
        for component in self.components.values():
            # Rastgele yük değişimi
            if random.random() < 0.01:  # %1 şans
                component.load_percentage = random.uniform(20, 100)
                component.is_running = component.load_percentage > 10
                
            # Metrikleri güncelle
            component.update_metrics(delta_time)
            
    def _check_faults_alarms(self):
        """Fault/Alarm kontrolü"""
        for component_id, component in self.components.items():
            # Fault kontrolü
            for fault_id, fault_info in self.fault_database.items():
                if fault_info["component"] == component_id:
                    threshold = fault_info["threshold"]
                    should_trigger = False
                    
                    # Threshold kontrolü
                    if fault_id == "F30001" and component.current > threshold:
                        should_trigger = True
                    elif fault_id == "F30002" and component.temperature > threshold:
                        should_trigger = True
                    elif fault_id == "F30011" and component.vibration > threshold:
                        should_trigger = True
                    elif fault_id == "F30020" and component.voltage > threshold:
                        should_trigger = True
                    elif fault_id == "F30030" and component.health_score < threshold:
                        should_trigger = True
                        
                    # Fault'u ekle/çıkar
                    if should_trigger and fault_id not in component.faults:
                        component.faults.append(fault_id)
                    elif not should_trigger and fault_id in component.faults:
                        component.faults.remove(fault_id)
                        
            # Alarm kontrolü
            for alarm_id, alarm_info in self.alarm_database.items():
                if alarm_info["component"] == component_id:
                    threshold = alarm_info["threshold"]
                    should_trigger = False
                    
                    # Threshold kontrolü
                    if alarm_id == "A05020" and component.temperature > threshold:
                        should_trigger = True
                    elif alarm_id == "A05030" and component.voltage > threshold:
                        should_trigger = True
                    elif alarm_id == "A05060" and component.vibration > threshold:
                        should_trigger = True
                        
                    # Alarm'ı ekle/çıkar
                    if should_trigger and alarm_id not in component.alarms:
                        component.alarms.append(alarm_id)
                    elif not should_trigger and alarm_id in component.alarms:
                        component.alarms.remove(alarm_id)
                        
    def _process_scenario(self):
        """Senaryoyu işle"""
        if not self._current_scenario:
            return
            
        # Senaryo süresi kontrolü
        elapsed = (datetime.now() - self._scenario_start_time).total_seconds()
        if elapsed > self._current_scenario["duration"]:
            self._current_scenario = None
            self._scenario_start_time = None
            return
            
        # Senaryo event'lerini işle
        for event in self._current_scenario.get("events", []):
            if elapsed >= event["time"] and not event.get("processed", False):
                self._process_scenario_event(event)
                event["processed"] = True
                
    def _process_scenario_event(self, event: Dict[str, Any]):
        """Senaryo event'ini işle"""
        event_type = event["type"]
        component_id = event.get("component")
        
        if event_type == "fault" and component_id in self.components:
            fault_id = event["fault_id"]
            component = self.components[component_id]
            if fault_id not in component.faults:
                component.faults.append(fault_id)
                
        elif event_type == "alarm" and component_id in self.components:
            alarm_id = event["alarm_id"]
            component = self.components[component_id]
            if alarm_id not in component.alarms:
                component.alarms.append(alarm_id)
                
        elif event_type == "load_change" and component_id in self.components:
            component = self.components[component_id]
            component.load_percentage = event["load_percentage"]
            component.is_running = component.load_percentage > 10
            
        elif event_type == "maintenance":
            # Bakım simülasyonu
            for component in self.components.values():
                component.health_score = min(100.0, component.health_score + 20.0)
                component.last_maintenance = datetime.now()
                component.maintenance_due = False
                
    def start_scenario(self, scenario_name: str):
        """Senaryo başlat"""
        scenarios = {
            "motor_overload": {
                "name": "Motor Overload Scenario",
                "description": "Motor aşırı yüklenme senaryosu",
                "duration": 300,  # 5 dakika
                "events": [
                    {"type": "load_change", "component": "motor", "load_percentage": 95, "time": 0},
                    {"type": "fault", "component": "motor", "fault_id": "F30001", "time": 60},
                    {"type": "alarm", "component": "motor", "alarm_id": "A05020", "time": 30}
                ]
            },
            "fan_failure": {
                "name": "Fan Failure Scenario", 
                "description": "Fan arızası senaryosu",
                "duration": 180,  # 3 dakika
                "events": [
                    {"type": "fault", "component": "fan", "fault_id": "F30030", "time": 0},
                    {"type": "alarm", "component": "fan", "alarm_id": "A05010", "time": 0}
                ]
            },
            "dc_link_problem": {
                "name": "DC Link Problem Scenario",
                "description": "DC Link voltaj problemi",
                "duration": 240,  # 4 dakika
                "events": [
                    {"type": "fault", "component": "dc_link", "fault_id": "F30020", "time": 0},
                    {"type": "alarm", "component": "dc_link", "alarm_id": "A05030", "time": 0}
                ]
            }
        }
        
        if scenario_name in scenarios:
            self._current_scenario = scenarios[scenario_name].copy()
            self._scenario_start_time = datetime.now()
            print(f"Started scenario: {self._current_scenario['name']}")
            return True
        return False
        
    def stop_scenario(self):
        """Senaryoyu durdur"""
        if self._current_scenario:
            print(f"Stopped scenario: {self._current_scenario['name']}")
            self._current_scenario = None
            self._scenario_start_time = None
            
    def get_current_scenario(self) -> Optional[Dict[str, Any]]:
        """Mevcut senaryoyu al"""
        if self._current_scenario and self._scenario_start_time:
            elapsed = (datetime.now() - self._scenario_start_time).total_seconds()
            remaining = max(0, self._current_scenario["duration"] - elapsed)
            
            return {
                "name": self._current_scenario["name"],
                "description": self._current_scenario["description"],
                "elapsed": elapsed,
                "remaining": remaining,
                "progress": (elapsed / self._current_scenario["duration"]) * 100
            }
        return None
        
    def read_diagnostics(self) -> Dict[str, Any]:
        """Teşhis verilerini oku"""
        faults = []
        alarms = []
        
        # Tüm bileşenlerden fault/alarm'ları topla
        for component_id, component in self.components.items():
            for fault_id in component.faults:
                fault_info = self.fault_database.get(fault_id, {})
                faults.append({
                    "id": fault_id,
                    "desc": fault_info.get("desc", f"Unknown fault {fault_id}"),
                    "component": component_id,
                    "severity": fault_info.get("severity", "unknown"),
                    "timestamp": datetime.now().isoformat()
                })
                
            for alarm_id in component.alarms:
                alarm_info = self.alarm_database.get(alarm_id, {})
                alarms.append({
                    "id": alarm_id,
                    "desc": alarm_info.get("desc", f"Unknown alarm {alarm_id}"),
                    "component": component_id,
                    "severity": alarm_info.get("severity", "unknown"),
                    "timestamp": datetime.now().isoformat()
                })
                
        return {
            "faults": faults,
            "alarms": alarms,
            "components": {cid: comp.get_status() for cid, comp in self.components.items()},
            "scenario": self.get_current_scenario(),
            "timestamp": datetime.now().isoformat()
        }
        
    def get_component_details(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Bileşen detaylarını al"""
        if component_id in self.components:
            component = self.components[component_id]
            return {
                "status": component.get_status(),
                "temperature_history": component.temperature_history[-20:],  # Son 20 veri
                "vibration_history": component.vibration_history[-20:],
                "health_history": component.health_history[-20:]
            }
        return None
        
    def inject_fault(self, fault_id: str, component_id: str):
        """Manuel fault enjeksiyonu"""
        if component_id in self.components and fault_id in self.fault_database:
            component = self.components[component_id]
            if fault_id not in component.faults:
                component.faults.append(fault_id)
                
    def inject_alarm(self, alarm_id: str, component_id: str):
        """Manuel alarm enjeksiyonu"""
        if component_id in self.components and alarm_id in self.alarm_database:
            component = self.components[component_id]
            if alarm_id not in component.alarms:
                component.alarms.append(alarm_id)
                
    def clear(self):
        """Tüm fault/alarm'ları temizle"""
        for component in self.components.values():
            component.faults.clear()
            component.alarms.clear()
            
    def perform_maintenance(self, component_id: str):
        """Bakım yap"""
        if component_id in self.components:
            component = self.components[component_id]
            component.health_score = 100.0
            component.last_maintenance = datetime.now()
            component.maintenance_due = False
            component.faults.clear()
            component.alarms.clear()
