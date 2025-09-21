"""
Simulator Control Panel - Simülatör kontrol paneli
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class SimulatorControlPanel:
    """Simülatör kontrol paneli"""
    
    def __init__(self, parent, simulator):
        self.parent = parent
        self.simulator = simulator
        
        self.window = tk.Toplevel(parent)
        self.window.title("Simulator Control Panel")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._update_status()
        
    def _create_widgets(self):
        """Widget'ları oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Advanced Simulator Control", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Senaryolar tab
        self._create_scenarios_tab()
        
        # Manuel kontrol tab
        self._create_manual_tab()
        
        # Durum tab
        self._create_status_tab()
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side="right")
                  
    def _create_scenarios_tab(self):
        """Senaryolar tab'ı oluştur"""
        scenarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(scenarios_frame, text="Scenarios")
        
        # Senaryo listesi
        list_frame = ttk.LabelFrame(scenarios_frame, text="Available Scenarios", padding="10")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ("Name", "Description", "Duration")
        self.scenarios_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.scenarios_tree.heading(col, text=col)
            self.scenarios_tree.column(col, width=150)
            
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.scenarios_tree.yview)
        self.scenarios_tree.configure(yscrollcommand=scrollbar.set)
        
        self.scenarios_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Senaryo butonları
        button_frame = ttk.Frame(scenarios_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Start Selected", 
                  command=self._start_selected_scenario).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Start Random", 
                  command=self._start_random_scenario).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Stop Scenario", 
                  command=self._stop_scenario).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Refresh", 
                  command=self._refresh_scenarios).pack(side="left")
        
        # Senaryoları yükle
        self._load_scenarios()
        
    def _create_manual_tab(self):
        """Manuel kontrol tab'ı oluştur"""
        manual_frame = ttk.Frame(self.notebook)
        self.notebook.add(manual_frame, text="Manual Control")
        
        # Fault injection
        fault_frame = ttk.LabelFrame(manual_frame, text="Fault Injection", padding="10")
        fault_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(fault_frame, text="Fault ID:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.fault_id_var = tk.StringVar(value="F30012")
        fault_ids = []
        if hasattr(self.simulator, 'fault_database'):
            fault_ids = list(self.simulator.fault_database.keys())
        fault_id_combo = ttk.Combobox(fault_frame, textvariable=self.fault_id_var,
                                     values=fault_ids,
                                     state="readonly", width=15)
        fault_id_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(fault_frame, text="Component:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.fault_comp_var = tk.StringVar(value="inverter")
        fault_comp_combo = ttk.Combobox(fault_frame, textvariable=self.fault_comp_var,
                                       values=["inverter", "motor", "rectifier", "dc_link", "fan", "cu320"],
                                       state="readonly", width=15)
        fault_comp_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(fault_frame, text="Inject Fault", 
                  command=self._inject_fault).grid(row=0, column=4)
        
        # Alarm injection
        alarm_frame = ttk.LabelFrame(manual_frame, text="Alarm Injection", padding="10")
        alarm_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(alarm_frame, text="Alarm ID:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.alarm_id_var = tk.StringVar(value="A05010")
        alarm_ids = []
        if hasattr(self.simulator, 'alarm_database'):
            alarm_ids = list(self.simulator.alarm_database.keys())
        alarm_id_combo = ttk.Combobox(alarm_frame, textvariable=self.alarm_id_var,
                                     values=alarm_ids,
                                     state="readonly", width=15)
        alarm_id_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(alarm_frame, text="Component:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.alarm_comp_var = tk.StringVar(value="fan")
        alarm_comp_combo = ttk.Combobox(alarm_frame, textvariable=self.alarm_comp_var,
                                       values=["inverter", "motor", "rectifier", "dc_link", "fan", "cu320"],
                                       state="readonly", width=15)
        alarm_comp_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(alarm_frame, text="Inject Alarm", 
                  command=self._inject_alarm).grid(row=0, column=4)
        
        # Rastgele işlemler
        random_frame = ttk.LabelFrame(manual_frame, text="Random Operations", padding="10")
        random_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(random_frame, text="Random Fault", 
                  command=self._random_fault).pack(side="left", padx=(0, 10))
        ttk.Button(random_frame, text="Random Alarm", 
                  command=self._random_alarm).pack(side="left", padx=(0, 10))
        ttk.Button(random_frame, text="Clear All", 
                  command=self._clear_all).pack(side="left", padx=(0, 10))
        
        # Stres testi
        stress_frame = ttk.LabelFrame(manual_frame, text="Stress Test", padding="10")
        stress_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(stress_frame, text="Duration (seconds):").pack(side="left", padx=(0, 10))
        self.stress_duration_var = tk.StringVar(value="60")
        stress_duration_entry = ttk.Entry(stress_frame, textvariable=self.stress_duration_var, width=10)
        stress_duration_entry.pack(side="left", padx=(0, 10))
        
        ttk.Button(stress_frame, text="Start Stress Test", 
                  command=self._start_stress_test).pack(side="left")
        
    def _create_status_tab(self):
        """Durum tab'ı oluştur"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        
        # Mevcut durum
        current_frame = ttk.LabelFrame(status_frame, text="Current Status", padding="10")
        current_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_text = tk.Text(current_frame, height=8, wrap="word")
        status_scrollbar = ttk.Scrollbar(current_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        status_scrollbar.pack(side="right", fill="y")
        
        # Güncelleme butonu
        ttk.Button(status_frame, text="Update Status", 
                  command=self._update_status).pack(pady=10)
        
    def _load_scenarios(self):
        """Senaryoları yükle"""
        # Treeview'ı temizle
        for item in self.scenarios_tree.get_children():
            self.scenarios_tree.delete(item)
            
        # Senaryoları ekle
        scenarios = self.simulator.get_available_scenarios()
        if isinstance(scenarios, dict):
            # RealisticSimulator formatı
            for scenario_id, scenario_name in scenarios.items():
                self.scenarios_tree.insert("", "end", values=(
                    scenario_name,
                    f"Scenario: {scenario_id}",
                    "Variable"
                ))
        else:
            # AdvancedSimulator formatı
            for scenario in scenarios:
                self.scenarios_tree.insert("", "end", values=(
                    scenario["name"],
                    scenario["description"],
                    f"{scenario['duration']}s"
                ))
            
    def _start_selected_scenario(self):
        """Seçili senaryoyu başlat"""
        selection = self.scenarios_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a scenario")
            return
            
        item = self.scenarios_tree.item(selection[0])
        scenario_name = item["values"][0]
        
        # RealisticSimulator için scenario_id'yi bul
        scenarios = self.simulator.get_available_scenarios()
        if isinstance(scenarios, dict):
            scenario_id = None
            for sid, sname in scenarios.items():
                if sname == scenario_name:
                    scenario_id = sid
                    break
            if scenario_id:
                if self.simulator.start_scenario(scenario_id):
                    messagebox.showinfo("Success", f"Scenario '{scenario_name}' started")
                    self._update_status()
                else:
                    messagebox.showerror("Error", f"Failed to start scenario '{scenario_name}'")
            else:
                messagebox.showerror("Error", "Scenario not found")
        else:
            if self.simulator.start_scenario(scenario_name):
                messagebox.showinfo("Success", f"Scenario '{scenario_name}' started")
                self._update_status()
            else:
                messagebox.showerror("Error", f"Failed to start scenario '{scenario_name}'")
            
    def _start_random_scenario(self):
        """Rastgele senaryo başlat"""
        if self.simulator.start_scenario():
            messagebox.showinfo("Success", "Random scenario started")
            self._update_status()
        else:
            messagebox.showerror("Error", "Failed to start random scenario")
            
    def _stop_scenario(self):
        """Senaryoyu durdur"""
        self.simulator.stop_scenario()
        messagebox.showinfo("Success", "Scenario stopped")
        self._update_status()
        
    def _refresh_scenarios(self):
        """Senaryoları yenile"""
        self._load_scenarios()
        
    def _inject_fault(self):
        """Fault injection"""
        fault_id = self.fault_id_var.get()
        component = self.fault_comp_var.get()
        self.simulator.inject_fault(fault_id, component)
        self._update_status()
        
    def _inject_alarm(self):
        """Alarm injection"""
        alarm_id = self.alarm_id_var.get()
        component = self.alarm_comp_var.get()
        self.simulator.inject_alarm(alarm_id, component)
        self._update_status()
        
    def _random_fault(self):
        """Rastgele fault"""
        if hasattr(self.simulator, 'random_fault'):
            self.simulator.random_fault()
        else:
            # RealisticSimulator için basit fault injection
            import random
            fault_ids = list(self.simulator.fault_database.keys()) if hasattr(self.simulator, 'fault_database') else ["F30012"]
            components = ["inverter", "motor", "rectifier", "dc_link", "fan", "cu320"]
            fault_id = random.choice(fault_ids)
            component = random.choice(components)
            self.simulator.inject_fault(fault_id, component)
        self._update_status()
        
    def _random_alarm(self):
        """Rastgele alarm"""
        if hasattr(self.simulator, 'random_alarm'):
            self.simulator.random_alarm()
        else:
            # RealisticSimulator için basit alarm injection
            import random
            alarm_ids = list(self.simulator.alarm_database.keys()) if hasattr(self.simulator, 'alarm_database') else ["A05010"]
            components = ["inverter", "motor", "rectifier", "dc_link", "fan", "cu320"]
            alarm_id = random.choice(alarm_ids)
            component = random.choice(components)
            self.simulator.inject_alarm(alarm_id, component)
        self._update_status()
        
    def _clear_all(self):
        """Tümünü temizle"""
        self.simulator.clear()
        self._update_status()
        
    def _start_stress_test(self):
        """Stres testi başlat"""
        try:
            duration = int(self.stress_duration_var.get())
            if hasattr(self.simulator, 'stress_test'):
                self.simulator.stress_test(duration)
                messagebox.showinfo("Success", f"Stress test started for {duration} seconds")
            else:
                messagebox.showinfo("Info", "Stress test not available for this simulator")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid duration")
            
    def _update_status(self):
        """Durumu güncelle"""
        diag = self.simulator.read_diagnostics()
        current_scenario = self.simulator.get_current_scenario()
        
        status_text = f"=== SIMULATOR STATUS ===\n"
        status_text += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Mevcut senaryo
        if current_scenario:
            status_text += f"Current Scenario: {current_scenario.get('name', 'Unknown')}\n"
            status_text += f"Description: {current_scenario.get('description', 'No description')}\n"
            status_text += f"Duration: {current_scenario.get('duration', 0)}s\n"
            status_text += f"Elapsed: {current_scenario.get('elapsed', 0):.1f}s\n"
            status_text += f"Remaining: {current_scenario.get('remaining', 0):.1f}s\n"
            status_text += f"Running: {current_scenario.get('running', False)}\n\n"
        else:
            status_text += "No active scenario\n\n"
            
        # Mevcut fault'lar
        status_text += f"Active Faults ({len(diag['faults'])}):\n"
        for fault in diag['faults']:
            status_text += f"  - {fault['id']}: {fault['desc']} ({fault['component']})\n"
        status_text += "\n"
        
        # Mevcut alarm'lar
        status_text += f"Active Alarms ({len(diag['alarms'])}):\n"
        for alarm in diag['alarms']:
            status_text += f"  - {alarm['id']}: {alarm['desc']} ({alarm['component']})\n"
        status_text += "\n"
        
        # Fault/Alarm veritabanı bilgileri
        if hasattr(self.simulator, 'fault_database'):
            status_text += f"Available Faults: {len(self.simulator.fault_database)}\n"
        if hasattr(self.simulator, 'alarm_database'):
            status_text += f"Available Alarms: {len(self.simulator.alarm_database)}\n"
        if hasattr(self.simulator, '_scenarios'):
            status_text += f"Available Scenarios: {len(self.simulator._scenarios)}\n"
        elif hasattr(self.simulator, 'get_available_scenarios'):
            scenarios = self.simulator.get_available_scenarios()
            if isinstance(scenarios, dict):
                status_text += f"Available Scenarios: {len(scenarios)}\n"
            else:
                status_text += f"Available Scenarios: {len(scenarios)}\n"
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_text)
        
    def show(self):
        """Pencereyi göster"""
        self.window.focus_set()
        self.window.wait_window()
