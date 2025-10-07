"""
Component Details Window - Bileşen detay penceresi
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class ComponentDetailsWindow:
    """Bileşen detay penceresi"""
    
    def __init__(self, parent, component_data: Dict[str, Any], history_data: List[Dict[str, Any]] = None, 
                 enhanced_data: Optional[Dict[str, Any]] = None, full_details: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.component_data = component_data
        self.history_data = history_data or []
        self.enhanced_data = enhanced_data
        self.full_details = full_details or {}
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Component Details - {component_data.get('name', 'Unknown')}")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._load_data()
        
    def _create_widgets(self):
        """Widget'ları oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, 
                               text=f"Component: {self.component_data.get('name', 'Unknown')}",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Genel bilgiler tab
        self._create_general_tab()
        
        # Geçmiş tab
        self._create_history_tab()
        
        # İstatistikler tab
        self._create_statistics_tab()
        
        # Enhanced data tab (eğer varsa)
        if self.enhanced_data:
            self._create_enhanced_tab()

        # Subcomponents tab (varsa)
        if self.full_details.get('subcomponents'):
            self._create_subcomponents_tab(self.full_details.get('subcomponents', []))

        # Checklist tab (varsa)
        if self.full_details.get('checklist'):
            self._create_checklist_tab(self.full_details.get('checklist', []))

        # Root-cause tab (varsa)
        if self.full_details.get('root_cause'):
            self._create_root_cause_tab(self.full_details.get('root_cause', []))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side="right")
                  
    def _create_general_tab(self):
        """Genel bilgiler tab'ı oluştur"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Scrollable frame
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bileşen bilgileri
        info_frame = ttk.LabelFrame(scrollable_frame, text="Component Information", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Bilgi satırları
        info_items = [
            ("ID:", self.component_data.get('id', 'N/A')),
            ("Name:", self.component_data.get('name', 'N/A')),
            ("Type:", self.component_data.get('type', 'N/A')),
            ("Position:", f"({self.component_data.get('x', 0)}, {self.component_data.get('y', 0)})"),
            ("Size:", f"{self.component_data.get('w', 0)} x {self.component_data.get('h', 0)}")
        ]
        
        for i, (label_text, value_text) in enumerate(info_items):
            label_frame = ttk.Frame(info_frame)
            label_frame.pack(fill="x", pady=2)
            
            ttk.Label(label_frame, text=label_text, width=10, anchor="w").pack(side="left")
            ttk.Label(label_frame, text=value_text, anchor="w").pack(side="left", padx=(10, 0))
        
        # Durum bilgileri
        status_frame = ttk.LabelFrame(scrollable_frame, text="Current Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Normal", font=("Arial", 12, "bold"))
        self.status_label.pack()
        
        # Son olaylar
        events_frame = ttk.LabelFrame(scrollable_frame, text="Recent Events", padding="10")
        events_frame.pack(fill="both", expand=True)
        
        # Treeview for events
        columns = ("Time", "Type", "Description")
        self.events_tree = ttk.Treeview(events_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=150)
            
        events_scrollbar = ttk.Scrollbar(events_frame, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=events_scrollbar.set)
        
        self.events_tree.pack(side="left", fill="both", expand=True)
        events_scrollbar.pack(side="right", fill="y")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_subcomponents_tab(self, subcomponents: List[Dict[str, Any]]):
        """Alt-komponentler tab'ı"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Subcomponents")
        tree = ttk.Treeview(tab, columns=("Name", "Metric", "Value"), show="headings")
        for col in ("Name", "Metric", "Value"):
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="w")
        for sc in subcomponents:
            name = sc.get('name', 'Unknown')
            metrics = sc.get('metrics', {})
            for k, v in metrics.items():
                tree.insert("", "end", values=(name, k, v))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _create_checklist_tab(self, checklist: List[Dict[str, Any]]):
        """Checklist tab'ı"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Checklist")
        tree = ttk.Treeview(tab, columns=("Item", "Status", "Hint"), show="headings")
        for col in ("Item", "Status", "Hint"):
            tree.heading(col, text=col)
            tree.column(col, width=180 if col != "Hint" else 280, anchor="w")
        for it in checklist:
            tree.insert("", "end", values=(it.get('item'), it.get('status'), it.get('hint')))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _create_root_cause_tab(self, findings: List[Dict[str, Any]]):
        """Root-cause önerileri tab'ı"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Root-cause")
        tree = ttk.Treeview(tab, columns=("Rule", "Severity", "Message", "Evidence"), show="headings")
        for col, width in (("Rule", 120), ("Severity", 90), ("Message", 240), ("Evidence", 260)):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="w")
        for f in findings:
            tree.insert("", "end", values=(f.get('rule'), f.get('severity'), f.get('message'), str(f.get('evidence'))))
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
    def _create_history_tab(self):
        """Geçmiş tab'ı oluştur"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="History")
        
        # Filtreler
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Filter by type:").pack(side="left", padx=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["all", "fault", "alarm", "clear", "connection", "user_action"],
                                   state="readonly", width=15)
        filter_combo.pack(side="left", padx=(0, 10))
        filter_combo.bind("<<ComboboxSelected>>", self._filter_history)
        
        # History treeview container
        tree_frame = ttk.Frame(history_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # History treeview
        history_columns = ("Timestamp", "Type", "Description", "Details")
        self.history_tree = ttk.Treeview(tree_frame, columns=history_columns, show="headings")
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
            
        history_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")
        
    def _create_statistics_tab(self):
        """İstatistikler tab'ı oluştur"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        # Scrollable frame
        canvas = tk.Canvas(stats_frame)
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Genel istatistikler
        general_stats_frame = ttk.LabelFrame(scrollable_frame, text="General Statistics", padding="10")
        general_stats_frame.pack(fill="x", pady=(0, 10))
        
        self.total_events_label = ttk.Label(general_stats_frame, text="Total Events: 0")
        self.total_events_label.pack(anchor="w")
        
        self.total_faults_label = ttk.Label(general_stats_frame, text="Total Faults: 0")
        self.total_faults_label.pack(anchor="w")
        
        self.total_alarms_label = ttk.Label(general_stats_frame, text="Total Alarms: 0")
        self.total_alarms_label.pack(anchor="w")
        
        # Günlük istatistikler
        daily_stats_frame = ttk.LabelFrame(scrollable_frame, text="Daily Statistics", padding="10")
        daily_stats_frame.pack(fill="x", pady=(0, 10))
        
        self.daily_avg_label = ttk.Label(daily_stats_frame, text="Daily Average: 0")
        self.daily_avg_label.pack(anchor="w")
        
        self.last_24h_label = ttk.Label(daily_stats_frame, text="Last 24h Events: 0")
        self.last_24h_label.pack(anchor="w")
        
        # En sık görülen olaylar
        frequent_events_frame = ttk.LabelFrame(scrollable_frame, text="Most Frequent Events", padding="10")
        frequent_events_frame.pack(fill="both", expand=True)
        
        self.frequent_events_text = tk.Text(frequent_events_frame, height=10, wrap="word")
        frequent_events_scrollbar = ttk.Scrollbar(frequent_events_frame, orient="vertical", 
                                                 command=self.frequent_events_text.yview)
        self.frequent_events_text.configure(yscrollcommand=frequent_events_scrollbar.set)
        
        self.frequent_events_text.pack(side="left", fill="both", expand=True)
        frequent_events_scrollbar.pack(side="right", fill="y")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _create_enhanced_tab(self):
        """Enhanced data tab'ı oluştur"""
        enhanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(enhanced_frame, text="Real-time Metrics")
        
        # Scrollable frame
        canvas = tk.Canvas(enhanced_frame)
        scrollbar = ttk.Scrollbar(enhanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Real-time metrics
        metrics_frame = ttk.LabelFrame(scrollable_frame, text="Real-time Metrics", padding="10")
        metrics_frame.pack(fill="x", pady=(0, 10))
        
        # Metrikleri grid layout ile göster
        metrics = [
            ("Health Score", f"{self.enhanced_data.get('health_score', 'N/A')}%"),
            ("Temperature", f"{self.enhanced_data.get('temperature', 'N/A')}°C"),
            ("Vibration", f"{self.enhanced_data.get('vibration', 'N/A')} mm/s"),
            ("Current", f"{self.enhanced_data.get('current', 'N/A')} A"),
            ("Voltage", f"{self.enhanced_data.get('voltage', 'N/A')} V"),
            ("Power", f"{self.enhanced_data.get('power', 'N/A')} kW"),
            ("Efficiency", f"{self.enhanced_data.get('efficiency', 'N/A')}%"),
            ("Load", f"{self.enhanced_data.get('load_percentage', 'N/A')}%"),
            ("Operating Hours", f"{self.enhanced_data.get('operating_hours', 'N/A')} h"),
            ("Fatigue Level", f"{self.enhanced_data.get('fatigue_level', 'N/A')}%"),
            ("Corrosion Level", f"{self.enhanced_data.get('corrosion_level', 'N/A')}%"),
            ("Lubrication Level", f"{self.enhanced_data.get('lubrication_level', 'N/A')}%"),
            ("Maintenance Due", "Yes" if self.enhanced_data.get('maintenance_due', False) else "No"),
            ("Days Since Maintenance", f"{self.enhanced_data.get('days_since_maintenance', 'N/A')} days"),
            ("Next Maintenance", f"{self.enhanced_data.get('next_maintenance_days', 'N/A')} days")
        ]
        
        for i, (label, value) in enumerate(metrics):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(metrics_frame, text=f"{label}:", font=("Arial", 9, "bold")).grid(
                row=row, column=col, sticky="w", padx=(0, 5), pady=2
            )
            ttk.Label(metrics_frame, text=value, font=("Arial", 9)).grid(
                row=row, column=col+1, sticky="w", padx=(0, 20), pady=2
            )
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _load_data(self):
        """Verileri yükle"""
        self._load_component_status()
        self._load_recent_events()
        self._load_history()
        self._load_statistics()
        
    def _load_component_status(self):
        """Bileşen durumunu yükle"""
        # Bu bileşenle ilgili son olayları kontrol et
        component_id = self.component_data.get('id', '')
        recent_events = [
            e for e in self.history_data[-10:]  # Son 10 olay
            if e.get('data', {}).get('component') == component_id
        ]
        
        if recent_events:
            last_event = recent_events[-1]
            if last_event['type'] == 'fault':
                self.status_label.config(text="FAULT", foreground="red")
            elif last_event['type'] == 'alarm':
                self.status_label.config(text="ALARM", foreground="orange")
            else:
                self.status_label.config(text="Normal", foreground="green")
        else:
            self.status_label.config(text="Normal", foreground="green")
            
    def _load_recent_events(self):
        """Son olayları yükle"""
        component_id = self.component_data.get('id', '')
        recent_events = [
            e for e in self.history_data[-20:]  # Son 20 olay
            if e.get('data', {}).get('component') == component_id
        ]
        
        # Treeview'ı temizle
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
            
        # Olayları ekle
        for event in reversed(recent_events[-10:]):  # En son 10 olay
            timestamp = datetime.fromisoformat(event['timestamp']).strftime('%H:%M:%S')
            event_type = event['type'].upper()
            description = event.get('description', '')
            
            self.events_tree.insert("", "end", values=(timestamp, event_type, description))
            
    def _load_history(self):
        """Geçmişi yükle"""
        self._filter_history()
        
    def _filter_history(self, event=None):
        """Geçmişi filtrele"""
        component_id = self.component_data.get('id', '')
        filter_type = self.filter_var.get()
        
        # Treeview'ı temizle
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Filtrelenmiş olayları al
        filtered_events = [
            e for e in self.history_data
            if e.get('data', {}).get('component') == component_id
            and (filter_type == "all" or e['type'] == filter_type)
        ]
        
        # Olayları ekle
        for event in reversed(filtered_events[-50:]):  # En son 50 olay
            timestamp = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            event_type = event['type'].upper()
            description = event.get('description', '')
            details = str(event.get('data', {}))
            
            self.history_tree.insert("", "end", values=(timestamp, event_type, description, details))
            
    def _load_statistics(self):
        """İstatistikleri yükle"""
        component_id = self.component_data.get('id', '')
        component_events = [
            e for e in self.history_data
            if e.get('data', {}).get('component') == component_id
        ]
        
        # Genel istatistikler
        total_events = len(component_events)
        total_faults = len([e for e in component_events if e['type'] == 'fault'])
        total_alarms = len([e for e in component_events if e['type'] == 'alarm'])
        
        self.total_events_label.config(text=f"Total Events: {total_events}")
        self.total_faults_label.config(text=f"Total Faults: {total_faults}")
        self.total_alarms_label.config(text=f"Total Alarms: {total_alarms}")
        
        # Günlük istatistikler
        if component_events:
            first_date = datetime.fromisoformat(component_events[0]['timestamp']).date()
            last_date = datetime.fromisoformat(component_events[-1]['timestamp']).date()
            days = (last_date - first_date).days + 1
            daily_avg = total_events / days if days > 0 else 0
            
            # Son 24 saat
            last_24h = datetime.now() - timedelta(hours=24)
            recent_24h = len([
                e for e in component_events
                if datetime.fromisoformat(e['timestamp']) > last_24h
            ])
        else:
            daily_avg = 0
            recent_24h = 0
            
        self.daily_avg_label.config(text=f"Daily Average: {daily_avg:.2f}")
        self.last_24h_label.config(text=f"Last 24h Events: {recent_24h}")
        
        # En sık görülen olaylar
        event_counts = {}
        for event in component_events:
            key = f"{event['type']}: {event.get('data', {}).get('id', 'Unknown')}"
            event_counts[key] = event_counts.get(key, 0) + 1
            
        # En sık görülen 10 olay
        sorted_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        self.frequent_events_text.delete(1.0, tk.END)
        for event, count in sorted_events:
            self.frequent_events_text.insert(tk.END, f"{event}: {count} times\n")
            
    def show(self):
        """Pencereyi göster"""
        self.window.focus_set()
        self.window.wait_window()
