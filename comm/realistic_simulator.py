"""
Realistic Simulator - Gerçekçi endüstriyel simülasyon
Gerçek SINAMICS sistemlerine çok yakın davranış
"""
import random
import time
import math
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


class EnvironmentalFactors:
    """Çevresel faktörler"""
    
    def __init__(self):
        self.ambient_temperature = 25.0  # Ortam sıcaklığı
        self.humidity = 50.0  # Nem %
        self.vibration_floor = 0.1  # Zemin titreşimi
        self.power_quality = 100.0  # Güç kalitesi %
        self.dust_level = 0.0  # Toz seviyesi
        
    def update(self, delta_time: float):
        """Çevresel faktörleri güncelle"""
        # Günlük sıcaklık değişimi (24 saatlik döngü)
        hour = datetime.now().hour
        daily_temp_variation = 5.0 * math.sin((hour - 6) * math.pi / 12)
        self.ambient_temperature = 25.0 + daily_temp_variation + random.uniform(-1, 1)
        
        # Nem değişimi
        self.humidity = max(30, min(80, 50 + random.uniform(-10, 10)))
        
        # Güç kalitesi (gerçek sistemlerde dalgalanır)
        self.power_quality = max(95, min(100, 100 + random.uniform(-3, 0)))
        
        # Toz seviyesi (zamanla artar)
        self.dust_level = min(100, self.dust_level + random.uniform(0, 0.1))


class ComponentHealth:
    """Bileşen sağlık modeli"""
    
    def __init__(self, component_id: str, component_name: str):
        self.component_id = component_id
        self.component_name = component_name
        
        # Fiziksel özellikler
        self.thermal_mass = random.uniform(0.8, 1.2)  # Termal kütle
        self.heat_capacity = random.uniform(0.9, 1.1)  # Isı kapasitesi
        self.efficiency_factor = random.uniform(0.95, 1.0)  # Verimlilik faktörü
        self.wear_rate = random.uniform(0.8, 1.2)  # Aşınma hızı
        
        # Durum değişkenleri
        self.temperature = 25.0
        self.target_temperature = 25.0
        self.vibration = 0.0
        self.current = 0.0
        self.voltage = 0.0
        self.power = 0.0
        self.efficiency = 100.0
        
        # Yük ve operasyon
        self.load_percentage = 0.0
        self.is_running = False
        self.operating_hours = 0.0
        self.start_stop_cycles = 0
        
        # Sağlık metrikleri
        self.health_score = 100.0
        self.fatigue_level = 0.0  # Yorulma seviyesi
        self.corrosion_level = 0.0  # Korozyon seviyesi
        self.lubrication_level = 100.0  # Yağlama seviyesi
        
        # Arıza durumu
        self.faults = []
        self.alarms = []
        self.maintenance_due = False
        self.last_maintenance = datetime.now()
        self.next_maintenance = datetime.now() + timedelta(days=30)
        
        # Trend verileri
        self.temperature_history = []
        self.vibration_history = []
        self.health_history = []
        self.efficiency_history = []
        
    def update(self, delta_time: float, env_factors: EnvironmentalFactors, 
               system_load: float, system_frequency: float):
        """Bileşeni güncelle"""
        
        # Yük değişimi (gerçek sistemlerde yavaş değişir)
        target_load = system_load * self.efficiency_factor
        load_change_rate = 2.0  # %/saniye
        if abs(target_load - self.load_percentage) > 1.0:
            if target_load > self.load_percentage:
                self.load_percentage = min(target_load, self.load_percentage + load_change_rate * delta_time)
            else:
                self.load_percentage = max(target_load, self.load_percentage - load_change_rate * delta_time)
        
        self.is_running = self.load_percentage > 5.0
        
        # Operasyon saatleri
        if self.is_running:
            self.operating_hours += delta_time / 3600.0  # Saat cinsinden
            
        # Sıcaklık hesaplama (gerçekçi termal model)
        self._update_temperature(delta_time, env_factors)
        
        # Titreşim hesaplama
        self._update_vibration(delta_time, env_factors)
        
        # Elektriksel parametreler
        self._update_electrical_parameters(delta_time, system_frequency)
        
        # Sağlık hesaplama
        self._update_health_metrics(delta_time, env_factors)
        
        # Aşınma ve yorulma
        self._update_wear_and_fatigue(delta_time)
        
        # Geçmiş verilerini güncelle
        self._update_history()
        
    def _update_temperature(self, delta_time: float, env_factors: EnvironmentalFactors):
        """Sıcaklık güncelleme (gerçekçi termal model)"""
        if self.is_running:
            # Yük bazlı ısı üretimi
            heat_generation = (self.load_percentage / 100.0) ** 1.5 * 50.0  # W
            
            # Verimlilik kaybından ısı
            efficiency_loss = (100.0 - self.efficiency) / 100.0 * 20.0
            
            # Aşınma kaynaklı ısı
            wear_heat = self.fatigue_level / 100.0 * 10.0
            
            # Toplam ısı üretimi
            total_heat = heat_generation + efficiency_loss + wear_heat
            
            # Termal kütle ile sıcaklık artışı
            temp_rise = (total_heat / (self.thermal_mass * self.heat_capacity)) * delta_time
            
            # Hedef sıcaklık
            self.target_temperature = env_factors.ambient_temperature + temp_rise
            
            # Sıcaklık değişimi (termal zaman sabiti)
            thermal_time_constant = 300.0  # 5 dakika
            temp_change = (self.target_temperature - self.temperature) / thermal_time_constant * delta_time
            self.temperature += temp_change
        else:
            # Soğuma (Newton's law of cooling)
            cooling_rate = 0.02  # °C/saniye
            temp_drop = (self.temperature - env_factors.ambient_temperature) * cooling_rate * delta_time
            self.temperature = max(env_factors.ambient_temperature, self.temperature - temp_drop)
            
    def _update_vibration(self, delta_time: float, env_factors: EnvironmentalFactors):
        """Titreşim güncelleme"""
        if self.is_running:
            # Temel titreşim (yük bazlı)
            base_vibration = (self.load_percentage / 100.0) * 3.0
            
            # Sağlık faktörü
            health_factor = (100.0 - self.health_score) / 100.0
            
            # Aşınma faktörü
            wear_factor = self.fatigue_level / 100.0
            
            # Çevresel faktörler
            env_vibration = env_factors.vibration_floor
            
            # Rastgele varyasyon (gerçek sistemlerde var)
            random_variation = random.uniform(-0.5, 0.5)
            
            # Toplam titreşim
            self.vibration = base_vibration + (health_factor * 5.0) + (wear_factor * 3.0) + env_vibration + random_variation
            self.vibration = max(0, self.vibration)
        else:
            self.vibration = env_factors.vibration_floor
            
    def _update_electrical_parameters(self, delta_time: float, system_frequency: float):
        """Elektriksel parametreleri güncelle"""
        if self.is_running:
            # Akım (yük bazlı)
            base_current = (self.load_percentage / 100.0) * 50.0  # A
            efficiency_factor = self.efficiency / 100.0
            self.current = base_current / efficiency_factor
            
            # Voltaj (güç kalitesi etkisi)
            base_voltage = 400.0  # V
            power_quality_factor = 100.0 / 100.0  # env_factors.power_quality / 100.0
            self.voltage = base_voltage * power_quality_factor
            
            # Güç
            self.power = self.current * self.voltage * math.sqrt(3) / 1000.0  # kW
            
            # Verimlilik (sağlık ve aşınma etkisi)
            health_efficiency = self.health_score / 100.0
            wear_efficiency = 1.0 - (self.fatigue_level / 100.0) * 0.1
            self.efficiency = 100.0 * health_efficiency * wear_efficiency
        else:
            self.current = 0.0
            self.voltage = 0.0
            self.power = 0.0
            
    def _update_health_metrics(self, delta_time: float, env_factors: EnvironmentalFactors):
        """Sağlık metriklerini güncelle"""
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
            
        # Çevresel etkiler
        env_factor = 1.0
        if env_factors.dust_level > 50:
            env_factor = max(0.0, 1.0 - (env_factors.dust_level - 50) / 50.0)
            
        # Sağlık değişimi
        health_change = (temp_factor + vib_factor + load_factor + env_factor) / 4.0 - 1.0
        self.health_score += health_change * 0.05  # Yavaş değişim
        self.health_score = max(0.0, min(100.0, self.health_score))
        
    def _update_wear_and_fatigue(self, delta_time: float):
        """Aşınma ve yorulma güncelleme"""
        if self.is_running:
            # Yorulma (yük ve süre bazlı)
            fatigue_rate = (self.load_percentage / 100.0) ** 2.0 * 0.01
            self.fatigue_level += fatigue_rate * delta_time
            
            # Korozyon (nem ve sıcaklık bazlı)
            corrosion_rate = 0.001 * (self.temperature / 50.0)
            self.corrosion_level += corrosion_rate * delta_time
            
            # Yağlama azalması
            lubrication_loss = 0.01 * (self.load_percentage / 100.0)
            self.lubrication_level = max(0, self.lubrication_level - lubrication_loss * delta_time)
            
        # Bakım gereksinimi kontrolü
        if (self.fatigue_level > 80 or 
            self.corrosion_level > 50 or 
            self.lubrication_level < 20 or
            self.health_score < 30):
            self.maintenance_due = True
            
    def _update_history(self):
        """Geçmiş verilerini güncelle"""
        current_time = datetime.now()
        
        # Son 100 veriyi sakla
        self.temperature_history.append((current_time, self.temperature))
        self.vibration_history.append((current_time, self.vibration))
        self.health_history.append((current_time, self.health_score))
        self.efficiency_history.append((current_time, self.efficiency))
        
        # Eski verileri temizle (1 saat)
        cutoff_time = current_time - timedelta(hours=1)
        self.temperature_history = [(t, v) for t, v in self.temperature_history if t > cutoff_time]
        self.vibration_history = [(t, v) for t, v in self.vibration_history if t > cutoff_time]
        self.health_history = [(t, v) for t, v in self.health_history if t > cutoff_time]
        self.efficiency_history = [(t, v) for t, v in self.efficiency_history if t > cutoff_time]
        
    def perform_maintenance(self):
        """Bakım yap"""
        self.health_score = min(100.0, self.health_score + 30.0)
        self.fatigue_level = max(0, self.fatigue_level - 50.0)
        self.corrosion_level = max(0, self.corrosion_level - 20.0)
        self.lubrication_level = 100.0
        self.last_maintenance = datetime.now()
        self.next_maintenance = datetime.now() + timedelta(days=30)
        self.maintenance_due = False
        self.faults.clear()
        self.alarms.clear()
        
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
            "efficiency": round(self.efficiency, 1),
            "load_percentage": round(self.load_percentage, 1),
            "is_running": self.is_running,
            "operating_hours": round(self.operating_hours, 1),
            "fatigue_level": round(self.fatigue_level, 1),
            "corrosion_level": round(self.corrosion_level, 1),
            "lubrication_level": round(self.lubrication_level, 1),
            "faults": len(self.faults),
            "alarms": len(self.alarms),
            "maintenance_due": self.maintenance_due,
            "days_since_maintenance": (datetime.now() - self.last_maintenance).days,
            "next_maintenance_days": (self.next_maintenance - datetime.now()).days
        }


class RealisticSimulator:
    """Gerçekçi simülatör"""
    
    def __init__(self):
        self.components = {}
        self.environment = EnvironmentalFactors()
        self._running = False
        self._thread = None
        self._last_update = datetime.now()
        
        # Sistem parametreleri
        self.system_load = 0.0  # Sistem yükü %
        self.system_frequency = 50.0  # Hz
        self.system_voltage = 400.0  # V
        
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
            {"id": "rectifier", "name": "Rectifier", "type": "power_conversion"},
            {"id": "dc_link", "name": "DC Link", "type": "energy_storage"},
            {"id": "inverter", "name": "Inverter", "type": "power_conversion"},
            {"id": "motor", "name": "Motor", "type": "mechanical"},
            {"id": "fan", "name": "Fan", "type": "cooling"},
            {"id": "cu320", "name": "CU320-2 PN", "type": "control"}
        ]
        
        for config in component_configs:
            self.components[config["id"]] = ComponentHealth(
                config["id"], config["name"]
            )
            
    def _setup_fault_alarm_database(self):
        """Fault/Alarm veritabanını kur"""
        self.fault_database = {
            "F30001": {"desc": "Motor overcurrent", "component": "motor", "severity": "high", "threshold": 60.0},
            "F30002": {"desc": "Motor overtemperature", "component": "motor", "severity": "high", "threshold": 75.0},
            "F30005": {"desc": "Rectifier overcurrent", "component": "rectifier", "severity": "high", "threshold": 55.0},
            "F30011": {"desc": "Motor bearing fault", "component": "motor", "severity": "medium", "threshold": 8.0},
            "F30012": {"desc": "Inverter overcurrent", "component": "inverter", "severity": "high", "threshold": 50.0},
            "F30020": {"desc": "DC link overvoltage", "component": "dc_link", "severity": "high", "threshold": 800.0},
            "F30021": {"desc": "DC link undervoltage", "component": "dc_link", "severity": "medium", "threshold": 350.0},
            "F30030": {"desc": "Fan failure", "component": "fan", "severity": "medium", "threshold": 15.0},
            "F30040": {"desc": "Control unit fault", "component": "cu320", "severity": "high", "threshold": 20.0},
            "F30050": {"desc": "Communication fault", "component": "cu320", "severity": "medium", "threshold": 10.0},
        }
        
        self.alarm_database = {
            "A05010": {"desc": "Fan speed low", "component": "fan", "severity": "low", "threshold": 5.0},
            "A05020": {"desc": "Motor temperature high", "component": "motor", "severity": "medium", "threshold": 65.0},
            "A05030": {"desc": "DC link voltage high", "component": "dc_link", "severity": "medium", "threshold": 750.0},
            "A05040": {"desc": "Inverter temperature high", "component": "inverter", "severity": "medium", "threshold": 70.0},
            "A05050": {"desc": "Communication warning", "component": "cu320", "severity": "low", "threshold": 3.0},
            "A05060": {"desc": "Motor bearing wear", "component": "motor", "severity": "low", "threshold": 6.0},
            "A05070": {"desc": "Maintenance due", "component": "system", "severity": "low", "threshold": 0.0},
            "A05080": {"desc": "Efficiency low", "component": "system", "severity": "medium", "threshold": 85.0},
        }
        
    def start(self):
        """Simülatörü başlat"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self._thread.start()
            print("Realistic Simulator started")
            
    def stop(self):
        """Simülatörü durdur"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("Realistic Simulator stopped")
        
    def _simulation_loop(self):
        """Ana simülasyon döngüsü"""
        while self._running:
            try:
                current_time = datetime.now()
                delta_time = (current_time - self._last_update).total_seconds()
                self._last_update = current_time
                
                # Çevresel faktörleri güncelle
                self.environment.update(delta_time)
                
                # Sistem yükünü güncelle (gerçekçi yük profili)
                self._update_system_load(delta_time)
                
                # Bileşenleri güncelle
                for component in self.components.values():
                    component.update(delta_time, self.environment, 
                                   self.system_load, self.system_frequency)
                
                # Fault/Alarm kontrolü
                self._check_faults_alarms()
                
                # Senaryo işleme
                if self._current_scenario:
                    self._process_scenario()
                    
                time.sleep(0.1)  # 100ms güncelleme
                
            except Exception as e:
                print(f"Simulation loop error: {e}")
                time.sleep(1.0)
                
    def _update_system_load(self, delta_time: float):
        """Sistem yükünü güncelle (gerçekçi yük profili)"""
        hour = datetime.now().hour
        
        # Günlük yük profili (gerçek fabrikalarda böyle)
        if 6 <= hour <= 8:  # Sabah başlangıç
            target_load = 30.0 + random.uniform(-5, 5)
        elif 8 <= hour <= 12:  # Sabah üretim
            target_load = 85.0 + random.uniform(-10, 5)
        elif 12 <= hour <= 13:  # Öğle molası
            target_load = 20.0 + random.uniform(-5, 5)
        elif 13 <= hour <= 17:  # Öğleden sonra üretim
            target_load = 90.0 + random.uniform(-5, 10)
        elif 17 <= hour <= 18:  # Akşam kapanış
            target_load = 40.0 + random.uniform(-10, 5)
        else:  # Gece
            target_load = 10.0 + random.uniform(-5, 5)
            
        # Yavaş yük değişimi (gerçek sistemlerde aniden değişmez)
        load_change_rate = 5.0  # %/saniye
        if abs(target_load - self.system_load) > 2.0:
            if target_load > self.system_load:
                self.system_load = min(target_load, self.system_load + load_change_rate * delta_time)
            else:
                self.system_load = max(target_load, self.system_load - load_change_rate * delta_time)
                
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
                    elif fault_id == "F30040" and component.fatigue_level > threshold:
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
                    elif alarm_id == "A05070" and component.maintenance_due:
                        should_trigger = True
                    elif alarm_id == "A05080" and component.efficiency < threshold:
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
        
        if event_type == "load_increase" and component_id in self.components:
            component = self.components[component_id]
            component.load_percentage = event["load_percentage"]
            
        elif event_type == "maintenance_skip":
            # Bakım atlama (gerçekçi senaryo)
            for component in self.components.values():
                component.fatigue_level += 20.0
                component.health_score -= 10.0
                
    def start_scenario(self, scenario_name: str = None):
        """Senaryo başlat"""
        scenarios = {
            "production_peak": {
                "name": "Production Peak Load",
                "description": "Maksimum üretim yükü senaryosu",
                "duration": 600,  # 10 dakika
                "events": [
                    {"type": "load_increase", "component": "motor", "load_percentage": 95, "time": 0},
                    {"type": "load_increase", "component": "inverter", "load_percentage": 90, "time": 0},
                ]
            },
            "maintenance_overdue": {
                "name": "Maintenance Overdue",
                "description": "Bakım gecikmesi senaryosu",
                "duration": 300,  # 5 dakika
                "events": [
                    {"type": "maintenance_skip", "time": 0},
                ]
            },
            "environmental_stress": {
                "name": "Environmental Stress",
                "description": "Çevresel stres senaryosu",
                "duration": 400,  # 6.7 dakika
                "events": [
                    {"type": "load_increase", "component": "fan", "load_percentage": 100, "time": 0},
                ]
            }
        }
        
        # Eğer scenario_name belirtilmemişse rastgele seç
        if scenario_name is None:
            scenario_name = random.choice(list(scenarios.keys()))
        
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
                "duration": self._current_scenario["duration"],  # Eksik olan alan
                "elapsed": elapsed,
                "remaining": remaining,
                "progress": (elapsed / self._current_scenario["duration"]) * 100,
                "running": remaining > 0  # Running durumu
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
            "environment": {
                "ambient_temperature": round(self.environment.ambient_temperature, 1),
                "humidity": round(self.environment.humidity, 1),
                "power_quality": round(self.environment.power_quality, 1),
                "dust_level": round(self.environment.dust_level, 1)
            },
            "system": {
                "load_percentage": round(self.system_load, 1),
                "frequency": self.system_frequency,
                "voltage": self.system_voltage
            },
            "scenario": self.get_current_scenario(),
            "timestamp": datetime.now().isoformat()
        }
        
    def get_component_details(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Bileşen detaylarını al"""
        if component_id in self.components:
            component = self.components[component_id]
            return {
                "status": component.get_status(),
                "temperature_history": component.temperature_history[-50:],  # Son 50 veri
                "vibration_history": component.vibration_history[-50:],
                "health_history": component.health_history[-50:],
                "efficiency_history": component.efficiency_history[-50:],
                "trends": self._calculate_trends(component)
            }
        return None
        
    def _calculate_trends(self, component: ComponentHealth) -> Dict[str, Any]:
        """Trend analizi"""
        if len(component.health_history) < 10:
            return {"health_trend": "stable", "temperature_trend": "stable"}
            
        # Sağlık trendi
        recent_health = [h[1] for h in component.health_history[-10:]]
        health_trend = "improving" if recent_health[-1] > recent_health[0] else "declining"
        
        # Sıcaklık trendi
        recent_temp = [t[1] for t in component.temperature_history[-10:]]
        temp_trend = "rising" if recent_temp[-1] > recent_temp[0] else "falling"
        
        return {
            "health_trend": health_trend,
            "temperature_trend": temp_trend,
            "health_change_rate": round(recent_health[-1] - recent_health[0], 2),
            "temperature_change_rate": round(recent_temp[-1] - recent_temp[0], 2)
        }
        
    def perform_maintenance(self, component_id: str):
        """Bakım yap"""
        if component_id in self.components:
            self.components[component_id].perform_maintenance()
            
    def inject_fault(self, fault_id: str, component_id: str):
        """Manuel fault enjeksiyonu"""
        if component_id in self.components:
            component = self.components[component_id]
            if fault_id not in component.faults:
                component.faults.append(fault_id)
                print(f"Injected fault {fault_id} to {component_id}")
                
    def inject_alarm(self, alarm_id: str, component_id: str):
        """Manuel alarm enjeksiyonu"""
        if component_id in self.components:
            component = self.components[component_id]
            if alarm_id not in component.alarms:
                component.alarms.append(alarm_id)
                print(f"Injected alarm {alarm_id} to {component_id}")
                
    def clear(self):
        """Tüm fault/alarm'ları temizle"""
        for component in self.components.values():
            component.faults.clear()
            component.alarms.clear()
            
    def get_available_scenarios(self):
        """Mevcut senaryoları al"""
        return {
            "production_peak": "Production Peak Load",
            "maintenance_overdue": "Maintenance Overdue", 
            "environmental_stress": "Environmental Stress"
        }
        
    def get_component_details(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Bileşen detaylarını al"""
        if component_id in self.components:
            component = self.components[component_id]
            return {
                "status": component.get_status(),
                "temperature_history": component.temperature_history[-50:],  # Son 50 veri
                "vibration_history": component.vibration_history[-50:],
                "health_history": component.health_history[-50:],
                "efficiency_history": component.efficiency_history[-50:],
                "trends": self._calculate_trends(component)
            }
        return None
