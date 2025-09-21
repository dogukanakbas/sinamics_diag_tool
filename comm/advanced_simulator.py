"""
Advanced Simulator - Gelişmiş simülasyon sistemi
Gerçekçi SINAMICS senaryoları ve dinamik durum değişimleri
"""
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading


class AdvancedSimulator:
    """Gelişmiş simülatör - gerçekçi senaryolar"""
    
    def __init__(self):
        self._faults = []
        self._alarms = []
        self._scenarios = []
        self._current_scenario = None
        self._scenario_start_time = None
        self._running = False
        self._thread = None
        
        # SINAMICS fault kodları ve açıklamaları
        self.fault_database = {
            "F30001": {"desc": "Motor overcurrent", "component": "motor", "severity": "high"},
            "F30002": {"desc": "Motor overtemperature", "component": "motor", "severity": "high"},
            "F30005": {"desc": "Rectifier overcurrent", "component": "rectifier", "severity": "high"},
            "F30011": {"desc": "Motor bearing fault", "component": "motor", "severity": "medium"},
            "F30012": {"desc": "Inverter overcurrent", "component": "inverter", "severity": "high"},
            "F30020": {"desc": "DC link overvoltage", "component": "dc_link", "severity": "high"},
            "F30021": {"desc": "DC link undervoltage", "component": "dc_link", "severity": "medium"},
            "F30030": {"desc": "Fan failure", "component": "fan", "severity": "medium"},
            "F30040": {"desc": "Control unit fault", "component": "cu320", "severity": "high"},
            "F30050": {"desc": "Communication fault", "component": "cu320", "severity": "medium"},
        }
        
        self.alarm_database = {
            "A05010": {"desc": "Fan speed low", "component": "fan", "severity": "low"},
            "A05020": {"desc": "Motor temperature high", "component": "motor", "severity": "medium"},
            "A05030": {"desc": "DC link voltage high", "component": "dc_link", "severity": "medium"},
            "A05040": {"desc": "Inverter temperature high", "component": "inverter", "severity": "medium"},
            "A05050": {"desc": "Communication warning", "component": "cu320", "severity": "low"},
            "A05060": {"desc": "Motor bearing wear", "component": "motor", "severity": "low"},
        }
        
        # Önceden tanımlı senaryolar
        self._setup_scenarios()
        
    def _setup_scenarios(self):
        """Senaryoları ayarla"""
        self._scenarios = [
            {
                "name": "Normal Operation",
                "description": "Normal çalışma durumu",
                "duration": 300,  # 5 dakika
                "events": []
            },
            {
                "name": "Motor Overload",
                "description": "Motor aşırı yüklenmesi senaryosu",
                "duration": 180,  # 3 dakika
                "events": [
                    {"time": 30, "type": "alarm", "id": "A05020", "component": "motor"},
                    {"time": 60, "type": "fault", "id": "F30001", "component": "motor"},
                    {"time": 120, "type": "clear", "target": "faults"}
                ]
            },
            {
                "name": "Cooling System Failure",
                "description": "Soğutma sistemi arızası",
                "duration": 240,  # 4 dakika
                "events": [
                    {"time": 20, "type": "alarm", "id": "A05010", "component": "fan"},
                    {"time": 40, "type": "alarm", "id": "A05040", "component": "inverter"},
                    {"time": 80, "type": "fault", "id": "F30030", "component": "fan"},
                    {"time": 120, "type": "fault", "id": "F30012", "component": "inverter"},
                    {"time": 180, "type": "clear", "target": "all"}
                ]
            },
            {
                "name": "DC Link Problems",
                "description": "DC link voltaj problemleri",
                "duration": 200,  # 3.3 dakika
                "events": [
                    {"time": 15, "type": "alarm", "id": "A05030", "component": "dc_link"},
                    {"time": 45, "type": "fault", "id": "F30020", "component": "dc_link"},
                    {"time": 90, "type": "clear", "target": "faults"},
                    {"time": 120, "type": "fault", "id": "F30021", "component": "dc_link"},
                    {"time": 150, "type": "clear", "target": "all"}
                ]
            },
            {
                "name": "Communication Issues",
                "description": "İletişim problemleri",
                "duration": 160,  # 2.7 dakika
                "events": [
                    {"time": 10, "type": "alarm", "id": "A05050", "component": "cu320"},
                    {"time": 30, "type": "fault", "id": "F30050", "component": "cu320"},
                    {"time": 60, "type": "clear", "target": "faults"},
                    {"time": 80, "type": "alarm", "id": "A05050", "component": "cu320"},
                    {"time": 120, "type": "clear", "target": "all"}
                ]
            },
            {
                "name": "Cascading Failures",
                "description": "Zincirleme arızalar",
                "duration": 300,  # 5 dakika
                "events": [
                    {"time": 20, "type": "alarm", "id": "A05060", "component": "motor"},
                    {"time": 40, "type": "fault", "id": "F30011", "component": "motor"},
                    {"time": 60, "type": "alarm", "id": "A05020", "component": "motor"},
                    {"time": 80, "type": "fault", "id": "F30002", "component": "motor"},
                    {"time": 100, "type": "fault", "id": "F30012", "component": "inverter"},
                    {"time": 120, "type": "fault", "id": "F30040", "component": "cu320"},
                    {"time": 200, "type": "clear", "target": "all"}
                ]
            }
        ]
        
    def start_scenario(self, scenario_name: Optional[str] = None):
        """Senaryo başlat"""
        if scenario_name:
            scenario = next((s for s in self._scenarios if s["name"] == scenario_name), None)
            if not scenario:
                print(f"Scenario '{scenario_name}' not found")
                return False
        else:
            scenario = random.choice(self._scenarios)
            
        self._current_scenario = scenario
        self._scenario_start_time = datetime.now()
        self._running = True
        
        print(f"Starting scenario: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Duration: {scenario['duration']} seconds")
        
        # Senaryo thread'ini başlat
        self._thread = threading.Thread(target=self._run_scenario, daemon=True)
        self._thread.start()
        
        return True
        
    def _run_scenario(self):
        """Senaryoyu çalıştır"""
        scenario = self._current_scenario
        start_time = self._scenario_start_time
        
        for event in scenario["events"]:
            if not self._running:
                break
                
            # Event zamanını bekle
            event_time = start_time + timedelta(seconds=event["time"])
            while datetime.now() < event_time and self._running:
                time.sleep(0.1)
                
            if not self._running:
                break
                
            # Event'i işle
            self._process_event(event)
            
        # Senaryo süresi dolduğunda temizle
        end_time = start_time + timedelta(seconds=scenario["duration"])
        while datetime.now() < end_time and self._running:
            time.sleep(0.1)
            
        if self._running:
            self.clear()
            print(f"Scenario '{scenario['name']}' completed")
            
    def _process_event(self, event: Dict[str, Any]):
        """Event'i işle"""
        event_type = event["type"]
        
        if event_type == "fault":
            fault_id = event["id"]
            component = event["component"]
            fault_info = self.fault_database.get(fault_id, {})
            
            fault_data = {
                "id": fault_id,
                "desc": fault_info.get("desc", "Unknown fault"),
                "component": component,
                "severity": fault_info.get("severity", "medium"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Aynı fault'u ekleme
            if not any(f["id"] == fault_id for f in self._faults):
                self._faults.append(fault_data)
                print(f"FAULT: {fault_id} - {fault_data['desc']} ({component})")
                
        elif event_type == "alarm":
            alarm_id = event["id"]
            component = event["component"]
            alarm_info = self.alarm_database.get(alarm_id, {})
            
            alarm_data = {
                "id": alarm_id,
                "desc": alarm_info.get("desc", "Unknown alarm"),
                "component": component,
                "severity": alarm_info.get("severity", "low"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Aynı alarm'ı ekleme
            if not any(a["id"] == alarm_id for a in self._alarms):
                self._alarms.append(alarm_data)
                print(f"ALARM: {alarm_id} - {alarm_data['desc']} ({component})")
                
        elif event_type == "clear":
            target = event.get("target", "all")
            if target == "all":
                self.clear()
                print("CLEAR: All faults and alarms cleared")
            elif target == "faults":
                self._faults.clear()
                print("CLEAR: All faults cleared")
            elif target == "alarms":
                self._alarms.clear()
                print("CLEAR: All alarms cleared")
                
    def stop_scenario(self):
        """Senaryoyu durdur"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Mevcut senaryoları al"""
        return [
            {
                "name": scenario["name"],
                "description": scenario["description"],
                "duration": scenario["duration"]
            }
            for scenario in self._scenarios
        ]
        
    def get_current_scenario(self) -> Optional[Dict[str, Any]]:
        """Mevcut senaryoyu al"""
        if not self._current_scenario:
            return None
            
        elapsed = (datetime.now() - self._scenario_start_time).total_seconds()
        return {
            "name": self._current_scenario["name"],
            "description": self._current_scenario["description"],
            "duration": self._current_scenario["duration"],
            "elapsed": elapsed,
            "remaining": self._current_scenario["duration"] - elapsed,
            "running": self._running
        }
        
    # Eski Simulator uyumluluğu için metodlar
    def inject_fault(self, fid="F30012", comp="inverter"):
        """Manuel fault injection"""
        fault_info = self.fault_database.get(fid, {})
        fault_data = {
            "id": fid,
            "desc": fault_info.get("desc", "Simulated fault"),
            "component": comp,
            "severity": fault_info.get("severity", "medium"),
            "timestamp": datetime.now().isoformat()
        }
        self._faults = [fault_data]
        print(f"MANUAL FAULT: {fid} - {fault_data['desc']} ({comp})")
        
    def inject_alarm(self, aid="A05010", comp="fan"):
        """Manuel alarm injection"""
        alarm_info = self.alarm_database.get(aid, {})
        alarm_data = {
            "id": aid,
            "desc": alarm_info.get("desc", "Simulated alarm"),
            "component": comp,
            "severity": alarm_info.get("severity", "low"),
            "timestamp": datetime.now().isoformat()
        }
        self._alarms = [alarm_data]
        print(f"MANUAL ALARM: {aid} - {alarm_data['desc']} ({comp})")
        
    def clear(self):
        """Tüm fault/alarm'ları temizle"""
        self._faults.clear()
        self._alarms.clear()
        print("MANUAL CLEAR: All faults and alarms cleared")
        
    def read_diagnostics(self):
        """Teşhis verilerini oku"""
        return {
            "faults": list(self._faults),
            "alarms": list(self._alarms),
            "scenario": self.get_current_scenario()
        }
        
    def random_fault(self):
        """Rastgele fault üret"""
        fault_id = random.choice(list(self.fault_database.keys()))
        fault_info = self.fault_database[fault_id]
        self.inject_fault(fault_id, fault_info["component"])
        
    def random_alarm(self):
        """Rastgele alarm üret"""
        alarm_id = random.choice(list(self.alarm_database.keys()))
        alarm_info = self.alarm_database[alarm_id]
        self.inject_alarm(alarm_id, alarm_info["component"])
        
    def stress_test(self, duration: int = 60):
        """Stres testi - hızlı fault/alarm üretimi"""
        def stress_worker():
            end_time = datetime.now() + timedelta(seconds=duration)
            while datetime.now() < end_time:
                if random.random() < 0.3:  # %30 ihtimal
                    if random.random() < 0.6:  # %60 fault, %40 alarm
                        self.random_fault()
                    else:
                        self.random_alarm()
                time.sleep(random.uniform(1, 3))  # 1-3 saniye arası
                
        thread = threading.Thread(target=stress_worker, daemon=True)
        thread.start()
        print(f"Stress test started for {duration} seconds")
