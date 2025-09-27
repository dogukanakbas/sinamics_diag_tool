import tkinter as tk
import os
import argparse
from ui.diagram import DriveDiagram
from ui.component_details import ComponentDetailsWindow
from comm.simulator import Simulator
from comm.advanced_simulator import AdvancedSimulator
from comm.enhanced_simulator import EnhancedSimulator
from comm.realistic_simulator import RealisticSimulator
from comm.command_adapter import CommandAdapter, TestAdapter
from comm.profinet_client import ProfinetClient
from comm.modbus_client import ModbusClient
from comm.connection_manager import ConnectionManager, EnhancedProfinetClient, EnhancedModbusClient
from utils.config import config
from utils.logger import logger
from utils.history import history
from utils.export_import import export_import
from utils.i18n import i18n
from utils.theme import theme
from utils.reporting import reporting
from security.auth import auth_manager, LoginWindow
from security.encryption import data_encryption, secure_config
from reporting.advanced_reporting import advanced_reporting
# OPC UA kullanacaksan: from comm.opcua_client import OPCUAClient

POLL_MS = config.get_poll_interval()

class App(tk.Tk):
    def __init__(self, model_path=None, adapter_cmd=None):
        super().__init__()
        
        # Güvenlik kontrolü - giriş yapmadan devam etme
        if not self._check_authentication():
            self.destroy()
            return
        
        # Konfigürasyonu yükle
        self._load_configuration()
        
        # UI ayarları
        self.title(i18n.get_app_title())
        window_size = config.get_window_size()
        self.geometry(f"{window_size[0]}x{window_size[1]}")
        
        # Model yolu belirle
        if model_path and os.path.exists(model_path):
            self.model_path = model_path
        else:
            self.model_path = config.get_default_model()
        
        # Diyagram oluştur
        self.diagram = DriveDiagram(self, self.model_path)
        self.diagram.pack(fill="both", expand=True)

        # --- Haberleşme katmanı seçimi ---
        self.data_source = self._create_data_source(adapter_cmd)
        
        # Menü oluştur
        self._create_menu()
        
        # Status bar oluştur
        self._create_status_bar()

        # Kısayol tuşları
        self._setup_keyboard_shortcuts()
        
        # Event binding
        self._setup_event_binding()

        # Polling başlat
        self.after(POLL_MS, self.poll)
        
        # Logging
        logger.info("Application started")
        logger.log_user_action("app_start", f"Model: {self.model_path}, User: {auth_manager.get_current_user().username if auth_manager.get_current_user() else 'Unknown'}")

    def _check_authentication(self):
        """Kimlik doğrulama kontrolü"""
        if not auth_manager.is_logged_in():
            login_window = LoginWindow(self, auth_manager)
            return login_window.show()
        return True
        
    def _load_configuration(self):
        """Konfigürasyonu yükle"""
        # Tema ayarla
        current_theme = config.get_theme()
        theme.set_theme(current_theme)
        
        # Dil ayarla
        current_language = config.get_language()
        i18n.set_language(current_language)
        
    def _create_status_bar(self):
        """Status bar oluştur"""
        if not config.get('ui.show_status_bar', True):
            return
            
        self.status_bar = tk.Frame(self, relief=tk.SUNKEN, bd=1, bg="#2d2d2d")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Sol taraf - bağlantı durumu ve kullanıcı bilgisi
        left_frame = tk.Frame(self.status_bar, bg="#2d2d2d")
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.connection_status = tk.Label(left_frame, text="Enhanced Simulator Mode", 
                                        relief=tk.SUNKEN, bd=1, anchor=tk.W, 
                                        bg="#2d2d2d", fg="#ffffff", font=("Arial", 9))
        self.connection_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # Kullanıcı bilgisi
        current_user = auth_manager.get_current_user()
        user_text = f"User: {current_user.username} ({current_user.role})" if current_user else "User: Unknown"
        self.user_status = tk.Label(left_frame, text=user_text, 
                                  relief=tk.SUNKEN, bd=1, anchor=tk.W,
                                  bg="#2d2d2d", fg="#cccccc", font=("Arial", 8))
        self.user_status.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Orta - Fault/Alarm sayıları
        self.fault_count = tk.Label(self.status_bar, text="Faults: 0", 
                                  relief=tk.SUNKEN, bd=1, anchor=tk.CENTER,
                                  bg="#2d2d2d", fg="#ff6b6b", font=("Arial", 9, "bold"))
        self.fault_count.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.alarm_count = tk.Label(self.status_bar, text="Alarms: 0", 
                                  relief=tk.SUNKEN, bd=1, anchor=tk.CENTER,
                                  bg="#2d2d2d", fg="#ffa726", font=("Arial", 9, "bold"))
        self.alarm_count.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Sağ taraf - zaman ve kısayollar
        right_frame = tk.Frame(self.status_bar, bg="#2d2d2d")
        right_frame.pack(side=tk.RIGHT)
        
        # Kısayollar
        shortcuts_text = "S:Scenario X:Stop P:Panel A:Alarm F:Fault C:Clear"
        self.shortcuts_label = tk.Label(right_frame, text=shortcuts_text, 
                                      relief=tk.SUNKEN, bd=1, anchor=tk.E,
                                      bg="#2d2d2d", fg="#888888", font=("Arial", 8))
        self.shortcuts_label.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Zaman
        self.time_label = tk.Label(right_frame, text="", relief=tk.SUNKEN, bd=1, anchor=tk.E,
                                 bg="#2d2d2d", fg="#ffffff", font=("Arial", 9))
        self.time_label.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Zaman güncelleme
        self._update_time()
        
    def _update_time(self):
        """Zamanı güncelle"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self._update_time)
        
    def _setup_event_binding(self):
        """Event binding'leri ayarla"""
        # Pencere kapatma
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Pencere boyutu değişikliği
        self.bind("<Configure>", self._on_window_configure)
        
        # Bileşen tıklama (diyagram üzerinde)
        self.diagram.canvas.bind("<Button-1>", self._on_component_click)

    def _create_data_source(self, adapter_cmd):
        """Veri kaynağını oluştur"""
        if adapter_cmd:
            # Command adapter kullan
            adapter = CommandAdapter(adapter_cmd)
            adapter.start()
            return adapter
        else:
            # Güvenli konfigürasyondan haberleşme ayarlarını al
            comm_config = secure_config.get_communication_credentials()
            
            # PROFINET kullanılıyorsa
            if comm_config.get('profinet', {}).get('enabled', False):
                profinet_config = comm_config['profinet']
                profinet_client = EnhancedProfinetClient(
                    plc_ip=profinet_config['plc_ip'],
                    rack=profinet_config['rack'],
                    slot=profinet_config['slot']
                )
                # Connection manager ile sarmala
                connection_manager = ConnectionManager(
                    profinet_client,
                    auto_reconnect=True,
                    reconnect_interval=30,
                    health_check_interval=60
                )
                connection_manager.start()
                return connection_manager
            
            # Modbus kullanılıyorsa
            elif comm_config.get('modbus', {}).get('enabled', False):
                modbus_config = comm_config['modbus']
                modbus_client = EnhancedModbusClient(
                    host=modbus_config['host'],
                    port=modbus_config['port'],
                    unit_id=modbus_config['unit_id']
                )
                # Connection manager ile sarmala
                connection_manager = ConnectionManager(
                    modbus_client,
                    auto_reconnect=True,
                    reconnect_interval=30,
                    health_check_interval=60
                )
                connection_manager.start()
                return connection_manager
            
            # Varsayılan: Gerçekçi simülatör kullan
            realistic_sim = RealisticSimulator()
            realistic_sim.start()
            return realistic_sim
            
    def _create_menu(self):
        """Menü çubuğu oluştur"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # macOS için menü çubuğunu zorla göster
        try:
            # macOS'ta menü çubuğu için özel ayar
            self.createcommand('tk::mac::ReopenApplication', lambda: self.deiconify())
        except:
            pass
        
        # File menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=i18n.get_menu_text("file"), menu=file_menu)
        file_menu.add_command(label=i18n.get_menu_text("load_model"), command=self._load_model)
        file_menu.add_separator()
        file_menu.add_command(label=i18n.get_menu_text("export_data"), command=self._export_data)
        file_menu.add_command(label=i18n.get_menu_text("import_data"), command=self._import_data)
        file_menu.add_separator()
        file_menu.add_command(label=i18n.get_menu_text("exit"), command=self._on_closing)
        
        # View menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=i18n.get_menu_text("view"), menu=view_menu)
        view_menu.add_command(label=i18n.get_menu_text("model_info"), command=self._show_model_info)
        view_menu.add_command(label=i18n.get_menu_text("connection_status"), command=self._show_connection_status)
        view_menu.add_separator()
        view_menu.add_command(label=i18n.get_menu_text("history"), command=self._show_history)
        view_menu.add_command(label=i18n.get_menu_text("statistics"), command=self._show_statistics)
        
        # Reports menüsü (gelişmiş raporlama)
        if auth_manager.has_permission('view_reports'):
            reports_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Reports", menu=reports_menu)
            reports_menu.add_command(label="Advanced Reports", command=self._show_advanced_reports)
            reports_menu.add_command(label="PDF Report", command=self._generate_pdf_report)
            reports_menu.add_command(label="Excel Report", command=self._generate_excel_report)
        
        # Simulator menüsü (sadece AdvancedSimulator için)
        if isinstance(self.data_source, AdvancedSimulator):
            simulator_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Simulator", menu=simulator_menu)
            simulator_menu.add_command(label="Control Panel", command=self._show_simulator_control)
            simulator_menu.add_separator()
            simulator_menu.add_command(label="Start Random Scenario", command=self._start_random_scenario)
            simulator_menu.add_command(label="Stop Scenario", command=self._stop_scenario)
        
        # Settings menüsü
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Tema alt menüsü
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        for theme_name in theme.get_available_themes():
            theme_menu.add_command(label=theme_name.title(), 
                                 command=lambda t=theme_name: self._change_theme(t))
        
        # Dil alt menüsü
        language_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Language", menu=language_menu)
        for lang in i18n.get_available_languages():
            language_menu.add_command(label=lang.upper(), 
                                    command=lambda l=lang: self._change_language(l))
        
        # Güvenlik menüsü (admin yetkisi gerekli)
        if auth_manager.has_permission('manage_users'):
            security_menu = tk.Menu(settings_menu, tearoff=0)
            settings_menu.add_cascade(label="Security", menu=security_menu)
            security_menu.add_command(label="User Management", command=self._show_user_management)
            security_menu.add_command(label="Change Password", command=self._change_password)
            security_menu.add_separator()
            security_menu.add_command(label="Logout", command=self._logout)
        
        # Help menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=i18n.get_menu_text("help"), menu=help_menu)
        help_menu.add_command(label=i18n.get_menu_text("shortcuts"), command=self._show_shortcuts)
        help_menu.add_command(label=i18n.get_menu_text("about"), command=self._show_about)

    def _setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        # Focus'u ana pencereye ver (tuşların çalışması için)
        self.focus_set()
        
        if isinstance(self.data_source, (Simulator, AdvancedSimulator, TestAdapter, EnhancedSimulator, RealisticSimulator)):
            # Simulator için kısayollar
            self.bind("<KeyPress-a>", lambda e: self.data_source.inject_alarm("A05010", "fan"))
            self.bind("<KeyPress-f>", lambda e: self.data_source.inject_fault("F30012", "inverter"))
            self.bind("<KeyPress-c>", lambda e: self.data_source.clear())
            
            # Gelişmiş simülatör için ek kısayollar
            if isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
                self.bind("<KeyPress-s>", lambda e: self._start_random_scenario())
                self.bind("<KeyPress-x>", lambda e: self._stop_scenario())
                self.bind("<KeyPress-p>", lambda e: self._show_simulator_control())
                self.bind("<KeyPress-h>", lambda e: self._start_healthy_scenario())
        else:
            # Diğer adaptörler için genel kısayollar
            self.bind("<F5>", lambda e: self._refresh_data())
            self.bind("<Control-r>", lambda e: self._refresh_data())
            
        # Her zaman çalışan kısayollar
        self.bind("<KeyPress-F5>", lambda e: self._refresh_data())
        self.bind("<Control-KeyPress-r>", lambda e: self._refresh_data())

    def _load_model(self):
        """Model dosyası yükle"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.join(os.path.dirname(__file__), "diag", "models")
        )
        if file_path:
            self.diagram.load_model(file_path)
            self.model_path = file_path

    def _show_model_info(self):
        """Model bilgilerini göster"""
        info = self.diagram.get_model_info()
        info_text = f"""Model Information:
Title: {info['title']}
Components: {info['components']}
Connections: {info['connections']}
Fault Mappings: {info['fault_mappings']}
Alarm Mappings: {info['alarm_mappings']}"""
        
        from tkinter import messagebox
        messagebox.showinfo("Model Information", info_text)

    def _show_connection_status(self):
        """Bağlantı durumunu göster"""
        if isinstance(self.data_source, CommandAdapter):
            status = "Connected" if self.data_source.test_connection() else "Disconnected"
            error = self.data_source.get_last_error()
            status_text = f"Connection Status: {status}"
            if error:
                status_text += f"\nLast Error: {error}"
        else:
            status_text = "Using Simulator Mode"
            
        from tkinter import messagebox
        messagebox.showinfo("Connection Status", status_text)

    def _show_shortcuts(self):
        """Klavye kısayollarını göster"""
        shortcuts = """Keyboard Shortcuts:
A - Inject Alarm (Simulator only)
F - Inject Fault (Simulator only)  
C - Clear All (Simulator only)
F5 - Refresh Data
Ctrl+R - Refresh Data"""
        
        # Gelişmiş simülatör için ek kısayollar
        if isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
            shortcuts += """
S - Start Random Scenario (Advanced/Enhanced/Realistic Simulator)
X - Stop Scenario (Advanced/Enhanced/Realistic Simulator)
P - Show Simulator Control Panel (Advanced/Enhanced/Realistic Simulator)
H - Start Healthy System Scenario (All Green)"""
        
        from tkinter import messagebox
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
        
    def _show_simulator_control(self):
        """Simülatör kontrol panelini göster"""
        if isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
            from ui.simulator_control import SimulatorControlPanel
            SimulatorControlPanel(self, self.data_source)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Simulator Control Panel is only available with Advanced/Enhanced/Realistic Simulator")
            
    def _start_random_scenario(self):
        """Rastgele senaryo başlat"""
        if isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
            if hasattr(self.data_source, 'start_scenario'):
                if self.data_source.start_scenario():
                    logger.log_user_action("start_scenario", "Random scenario started")
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Error", "Failed to start random scenario")
            else:
                from tkinter import messagebox
                messagebox.showinfo("Info", "This simulator doesn't support scenarios")
        else:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Scenarios are only available with Advanced/Enhanced/Realistic Simulator")
            
    def _stop_scenario(self):
        """Senaryoyu durdur"""
        if isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
            if hasattr(self.data_source, 'stop_scenario'):
                self.data_source.stop_scenario()
                logger.log_user_action("stop_scenario", "Scenario stopped")
            else:
                from tkinter import messagebox
                messagebox.showinfo("Info", "This simulator doesn't support scenarios")
        else:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Scenarios are only available with Advanced/Enhanced/Realistic Simulator")
            
    def _start_healthy_scenario(self):
        """Sağlıklı sistem senaryosunu başlat"""
        if isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
            if hasattr(self.data_source, 'start_scenario'):
                if self.data_source.start_scenario("healthy_system"):
                    logger.log_user_action("start_scenario", "Healthy system scenario started")
                    from tkinter import messagebox
                    messagebox.showinfo("Healthy System", "✅ Tüm sistem sağlıklı!\n\n• Tüm fault'lar temizlendi\n• Tüm alarm'lar temizlendi\n• Optimal koşullar ayarlandı\n• Sistem %100 sağlıklı")
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Error", "Failed to start healthy system scenario")
            else:
                from tkinter import messagebox
                messagebox.showinfo("Info", "This simulator doesn't support scenarios")
        else:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Scenarios are only available with Advanced/Enhanced/Realistic Simulator")

    def _show_about(self):
        """Hakkında bilgisi göster"""
        about_info = i18n.get_about_info()
        about_text = f"""{about_info['title']}
Version: {i18n.get_app_version()}
{about_info['description']}

Features:
{chr(10).join(f"- {feature}" for feature in about_info['features'])}"""
        
        from tkinter import messagebox
        messagebox.showinfo(about_info['title'], about_text)
        
    def _export_data(self):
        """Veri dışa aktar"""
        current_data = self.diagram.current
        file_path = export_import.show_export_dialog(self, current_data)
        if file_path:
            logger.log_user_action("export_data", f"File: {file_path}")
            
    def _import_data(self):
        """Veri içe aktar"""
        data = export_import.show_import_dialog(self)
        if data:
            self.diagram.update_status(data)
            logger.log_user_action("import_data", f"Data imported: {len(data.get('faults', []))} faults, {len(data.get('alarms', []))} alarms")
            
    def _show_history(self):
        """Geçmiş penceresi göster"""
        from tkinter import Toplevel, ttk
        import tkinter as tk
        
        history_window = Toplevel(self)
        history_window.title("Diagnostic History")
        history_window.geometry("800x600")
        history_window.transient(self)
        
        # Filtreler
        filter_frame = ttk.Frame(history_window)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Filter:").pack(side="left", padx=(0, 10))
        
        filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(filter_frame, textvariable=filter_var,
                                   values=["all", "fault", "alarm", "clear", "connection", "user_action"],
                                   state="readonly", width=15)
        filter_combo.pack(side="left", padx=(0, 10))
        
        # Treeview
        columns = ("Timestamp", "Type", "Description", "Details")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))
        
        def update_history():
            tree.delete(*tree.get_children())
            filter_type = filter_var.get()
            
            entries = history.get_recent_entries(100)
            if filter_type != "all":
                entries = [e for e in entries if e['type'] == filter_type]
                
            for entry in reversed(entries):
                timestamp = entry['timestamp'][:19]  # Sadece tarih-saat
                tree.insert("", "end", values=(
                    timestamp,
                    entry['type'].upper(),
                    entry.get('description', ''),
                    str(entry.get('data', {}))
                ))
                
        filter_combo.bind("<<ComboboxSelected>>", lambda e: update_history())
        update_history()
        
    def _show_statistics(self):
        """İstatistikler penceresi göster"""
        reporting.show_reporting_dialog(self, history.history)
        
    def _show_advanced_reports(self):
        """Gelişmiş raporlama penceresi göster"""
        if auth_manager.has_permission('view_reports'):
            advanced_reporting.show_reporting_dialog(self, history.history)
        else:
            messagebox.showerror("Access Denied", "You don't have permission to view reports")
            
    def _generate_pdf_report(self):
        """PDF raporu oluştur"""
        if auth_manager.has_permission('view_reports'):
            try:
                result = advanced_reporting.generate_comprehensive_report(history.history, "daily")
                if result['pdf_path']:
                    messagebox.showinfo("Success", f"PDF report generated: {result['pdf_path']}")
                else:
                    messagebox.showerror("Error", "Failed to generate PDF report")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF report: {e}")
        else:
            messagebox.showerror("Access Denied", "You don't have permission to generate reports")
            
    def _generate_excel_report(self):
        """Excel raporu oluştur"""
        if auth_manager.has_permission('view_reports'):
            try:
                result = advanced_reporting.generate_comprehensive_report(history.history, "daily")
                if result['excel_path']:
                    messagebox.showinfo("Success", f"Excel report generated: {result['excel_path']}")
                else:
                    messagebox.showerror("Error", "Failed to generate Excel report")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate Excel report: {e}")
        else:
            messagebox.showerror("Access Denied", "You don't have permission to generate reports")
            
    def _show_user_management(self):
        """Kullanıcı yönetimi penceresi göster"""
        if auth_manager.has_permission('manage_users'):
            from tkinter import Toplevel, ttk, messagebox
            import tkinter as tk
            
            user_window = Toplevel(self)
            user_window.title("User Management")
            user_window.geometry("600x400")
            user_window.transient(self)
            
            # Ana frame
            main_frame = ttk.Frame(user_window, padding="10")
            main_frame.pack(fill="both", expand=True)
            
            # Kullanıcı listesi
            ttk.Label(main_frame, text="Users:", font=("Arial", 12, "bold")).pack(anchor="w")
            
            # Treeview
            columns = ("Username", "Role", "Full Name", "Email", "Active", "Last Login")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
                
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True, pady=(10, 0))
            scrollbar.pack(side="right", fill="y", pady=(10, 0))
            
            # Butonlar
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            def refresh_users():
                tree.delete(*tree.get_children())
                users = auth_manager.list_users()
                for user in users:
                    last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
                    tree.insert("", "end", values=(
                        user.username,
                        user.role,
                        user.full_name,
                        user.email,
                        "Yes" if user.is_active else "No",
                        last_login
                    ))
                    
            def add_user():
                # Basit kullanıcı ekleme dialog'u
                dialog = tk.Toplevel(user_window)
                dialog.title("Add User")
                dialog.geometry("300x200")
                dialog.transient(user_window)
                dialog.grab_set()
                
                frame = ttk.Frame(dialog, padding="10")
                frame.pack(fill="both", expand=True)
                
                ttk.Label(frame, text="Username:").pack(anchor="w")
                username_var = tk.StringVar()
                ttk.Entry(frame, textvariable=username_var).pack(fill="x", pady=(0, 10))
                
                ttk.Label(frame, text="Password:").pack(anchor="w")
                password_var = tk.StringVar()
                ttk.Entry(frame, textvariable=password_var, show="*").pack(fill="x", pady=(0, 10))
                
                ttk.Label(frame, text="Role:").pack(anchor="w")
                role_var = tk.StringVar(value="operator")
                role_combo = ttk.Combobox(frame, textvariable=role_var, 
                                        values=["operator", "engineer", "admin"],
                                        state="readonly")
                role_combo.pack(fill="x", pady=(0, 10))
                
                def save_user():
                    if auth_manager.create_user(username_var.get(), password_var.get(), role_var.get()):
                        messagebox.showinfo("Success", "User created successfully")
                        refresh_users()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to create user")
                        
                ttk.Button(frame, text="Create", command=save_user).pack(pady=(10, 0))
                
            ttk.Button(button_frame, text="Add User", command=add_user).pack(side="left", padx=(0, 10))
            ttk.Button(button_frame, text="Refresh", command=refresh_users).pack(side="left")
            
            refresh_users()
        else:
            messagebox.showerror("Access Denied", "You don't have permission to manage users")
            
    def _change_password(self):
        """Şifre değiştir"""
        from tkinter import simpledialog
        
        current_user = auth_manager.get_current_user()
        if not current_user:
            return
            
        old_password = simpledialog.askstring("Change Password", "Enter current password:", show='*')
        if not old_password:
            return
            
        new_password = simpledialog.askstring("Change Password", "Enter new password:", show='*')
        if not new_password:
            return
            
        if auth_manager.change_password(current_user.username, old_password, new_password):
            messagebox.showinfo("Success", "Password changed successfully")
        else:
            messagebox.showerror("Error", "Failed to change password")
            
    def _logout(self):
        """Çıkış yap"""
        auth_manager.logout()
        messagebox.showinfo("Logout", "You have been logged out")
        self.destroy()
        
    def _change_theme(self, theme_name):
        """Tema değiştir"""
        theme.set_theme(theme_name)
        config.set_theme(theme_name)
        config.save()
        
        # UI'yi yenile
        self.diagram.draw()
        logger.log_user_action("change_theme", f"Theme: {theme_name}")
        
    def _change_language(self, language):
        """Dil değiştir"""
        i18n.set_language(language)
        config.set_language(language)
        config.save()
        
        # Menüyü yenile
        self._create_menu()
        logger.log_user_action("change_language", f"Language: {language}")
        
    def _on_component_click(self, event):
        """Bileşen tıklama olayı"""
        # Canvas'ta tıklanan item'ı bul
        clicked_items = self.diagram.canvas.find_closest(event.x, event.y)
        if not clicked_items:
            return
            
        clicked_item = clicked_items[0]
        
        # Component tag'ini kontrol et
        tags = self.diagram.canvas.gettags(clicked_item)
        component_id = None
        
        for tag in tags:
            if tag.startswith("component_"):
                component_id = tag.replace("component_", "")
                break
                
        if component_id:
            # Component'i bul
            clicked_component = None
            for component in self.diagram.model.get("components", []):
                if component["id"] == component_id:
                    clicked_component = component
                    break
                    
            if clicked_component:
                # Bileşen detay penceresini aç
                try:
                    # Enhanced data'yı al
                    enhanced_data = None
                    if hasattr(self.data_source, 'get_component_details'):
                        component_details = self.data_source.get_component_details(component_id)
                        if component_details and 'status' in component_details:
                            enhanced_data = component_details['status']
                    
                    ComponentDetailsWindow(self, clicked_component, list(history.history), enhanced_data)
                    logger.log_user_action("component_click", f"Component: {clicked_component.get('name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Error opening component details: {e}")
                    messagebox.showerror("Error", f"Failed to open component details: {e}")
            
    def _on_window_configure(self, event):
        """Pencere boyutu değişikliği"""
        if event.widget == self:
            config.set_window_size(event.width, event.height)
            
    def _on_closing(self):
        """Uygulama kapanırken"""
        logger.info("Application closing")
        logger.log_user_action("app_close", "Application closed by user")
        
        # Konfigürasyonu kaydet
        config.save()
        
        # Command adapter'ı durdur
        if isinstance(self.data_source, CommandAdapter):
            self.data_source.stop()
            
        # Uygulamayı kapat
        self.destroy()

    def _refresh_data(self):
        """Veriyi yenile"""
        if hasattr(self.data_source, 'read_diagnostics'):
            diag = self.data_source.read_diagnostics()
            self.diagram.update_status(diag)

    def poll(self):
        """Ana polling döngüsü"""
        try:
            diag = self.data_source.read_diagnostics()
            
            # Geçmiş verilerini karşılaştır
            previous_diag = self.diagram.current
            
            # Yeni fault'ları logla
            for fault in diag.get('faults', []):
                if fault not in previous_diag.get('faults', []):
                    history.add_fault(fault)
                    logger.log_diagnostic({'type': 'fault', 'data': fault})
                    
            # Yeni alarm'ları logla
            for alarm in diag.get('alarms', []):
                if alarm not in previous_diag.get('alarms', []):
                    history.add_alarm(alarm)
                    logger.log_diagnostic({'type': 'alarm', 'data': alarm})
                    
            # Temizleme olayını logla
            if len(previous_diag.get('faults', [])) > 0 and len(diag.get('faults', [])) == 0:
                history.add_clear_event(['faults'])
            if len(previous_diag.get('alarms', [])) > 0 and len(diag.get('alarms', [])) == 0:
                history.add_clear_event(['alarms'])
            
            # UI'yi güncelle
            self.diagram.update_status(diag)
            
            # Status bar'ı güncelle
            if hasattr(self, 'connection_status'):
                # Bağlantı durumu
                if isinstance(self.data_source, CommandAdapter):
                    status = "Command Adapter - Connected" if self.data_source.test_connection() else "Command Adapter - Disconnected"
                    self.connection_status.config(text=status)
                elif isinstance(self.data_source, (AdvancedSimulator, EnhancedSimulator, RealisticSimulator)):
                    if hasattr(self.data_source, 'get_current_scenario'):
                        current_scenario = self.data_source.get_current_scenario()
                        if current_scenario:
                            status = f"Scenario: {current_scenario['name']} ({current_scenario['remaining']:.0f}s)"
                        else:
                            if isinstance(self.data_source, RealisticSimulator):
                                status = "Realistic Simulator - Ready"
                            elif isinstance(self.data_source, EnhancedSimulator):
                                status = "Enhanced Simulator - Ready"
                            else:
                                status = "Advanced Simulator - Ready"
                    else:
                        if isinstance(self.data_source, RealisticSimulator):
                            status = "Realistic Simulator - Ready"
                        elif isinstance(self.data_source, EnhancedSimulator):
                            status = "Enhanced Simulator - Ready"
                        else:
                            status = "Advanced Simulator - Ready"
                    self.connection_status.config(text=status)
                elif hasattr(self.data_source, 'get_connection_status'):
                    conn_status = self.data_source.get_connection_status()
                    if conn_status.get('connected', False):
                        status = f"Connected - {type(self.data_source).__name__}"
                    else:
                        status = f"Disconnected - {type(self.data_source).__name__}"
                    self.connection_status.config(text=status)
                else:
                    self.connection_status.config(text="Simulator Mode")
                
                # Fault/Alarm sayılarını güncelle
                if hasattr(self, 'fault_count') and hasattr(self, 'alarm_count'):
                    fault_count = len(diag.get('faults', []))
                    alarm_count = len(diag.get('alarms', []))
                    
                    self.fault_count.config(text=f"Faults: {fault_count}")
                    self.alarm_count.config(text=f"Alarms: {alarm_count}")
                    
                    # Renk güncelleme
                    if fault_count > 0:
                        self.fault_count.config(fg="#ff4444")  # Kırmızı
                    else:
                        self.fault_count.config(fg="#ff6b6b")  # Açık kırmızı
                        
                    if alarm_count > 0:
                        self.alarm_count.config(fg="#ff8800")  # Turuncu
                    else:
                        self.alarm_count.config(fg="#ffa726")  # Açık turuncu
                    
        except Exception as e:
            logger.error(f"Polling error: {e}", e)
        finally:
            self.after(POLL_MS, self.poll)

    def __del__(self):
        """Uygulama kapanırken temizlik"""
        if isinstance(self.data_source, CommandAdapter):
            self.data_source.stop()

def parse_args():
    """Komut satırı argümanlarını parse et"""
    parser = argparse.ArgumentParser(description="SINAMICS Diag & Viz (Enhanced)")
    parser.add_argument("--model", help="Model JSON file path")
    parser.add_argument("--adapter", help="Command adapter command")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    app = App(model_path=args.model, adapter_cmd=args.adapter)
    app.mainloop()
