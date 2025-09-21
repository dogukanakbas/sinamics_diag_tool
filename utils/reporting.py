"""
Reporting System - Grafik raporlama ve istatistik sistemi
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict, Counter


class ReportingManager:
    """Raporlama yöneticisi"""
    
    def __init__(self):
        self.reports_dir = "reports"
        self._ensure_reports_dir()
        
    def _ensure_reports_dir(self):
        """Raporlar klasörünü oluştur"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
            
    def generate_fault_trend_chart(self, history_data: List[Dict[str, Any]], days: int = 7) -> str:
        """Fault trend grafiği oluştur"""
        try:
            # Son N günün verilerini filtrele
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = [
                entry for entry in history_data
                if datetime.fromisoformat(entry['timestamp']) > cutoff_date
            ]
            
            # Günlük fault sayılarını hesapla
            daily_faults = defaultdict(int)
            for entry in recent_data:
                if entry['type'] == 'fault':
                    date = datetime.fromisoformat(entry['timestamp']).date()
                    daily_faults[date] += 1
                    
            # Grafik oluştur
            dates = sorted(daily_faults.keys())
            fault_counts = [daily_faults[date] for date in dates]
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, fault_counts, marker='o', linewidth=2, markersize=6)
            plt.title(f'Fault Trend - Last {days} Days', fontsize=14, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Number of Faults', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Dosyaya kaydet
            filename = f"fault_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.reports_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"Error generating fault trend chart: {e}")
            return None
            
    def generate_component_analysis(self, history_data: List[Dict[str, Any]]) -> str:
        """Bileşen analiz grafiği oluştur"""
        try:
            # Fault'ları bileşenlere göre grupla
            component_faults = defaultdict(int)
            component_alarms = defaultdict(int)
            
            for entry in history_data:
                if entry['type'] in ['fault', 'alarm']:
                    data = entry['data']
                    component = data.get('component', 'Unknown')
                    
                    if entry['type'] == 'fault':
                        component_faults[component] += 1
                    else:
                        component_alarms[component] += 1
                        
            # Grafik oluştur
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Fault grafiği
            if component_faults:
                components = list(component_faults.keys())
                fault_counts = list(component_faults.values())
                
                ax1.bar(components, fault_counts, color='#ef4444', alpha=0.7)
                ax1.set_title('Faults by Component', fontweight='bold')
                ax1.set_ylabel('Number of Faults')
                ax1.tick_params(axis='x', rotation=45)
                
            # Alarm grafiği
            if component_alarms:
                components = list(component_alarms.keys())
                alarm_counts = list(component_alarms.values())
                
                ax2.bar(components, alarm_counts, color='#f59e0b', alpha=0.7)
                ax2.set_title('Alarms by Component', fontweight='bold')
                ax2.set_ylabel('Number of Alarms')
                ax2.tick_params(axis='x', rotation=45)
                
            plt.tight_layout()
            
            # Dosyaya kaydet
            filename = f"component_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.reports_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"Error generating component analysis: {e}")
            return None
            
    def generate_hourly_distribution(self, history_data: List[Dict[str, Any]]) -> str:
        """Saatlik dağılım grafiği oluştur"""
        try:
            # Saatlik fault/alarm sayılarını hesapla
            hourly_faults = defaultdict(int)
            hourly_alarms = defaultdict(int)
            
            for entry in history_data:
                if entry['type'] in ['fault', 'alarm']:
                    hour = datetime.fromisoformat(entry['timestamp']).hour
                    
                    if entry['type'] == 'fault':
                        hourly_faults[hour] += 1
                    else:
                        hourly_alarms[hour] += 1
                        
            # Grafik oluştur
            hours = list(range(24))
            fault_counts = [hourly_faults[h] for h in hours]
            alarm_counts = [hourly_alarms[h] for h in hours]
            
            plt.figure(figsize=(12, 6))
            plt.plot(hours, fault_counts, marker='o', label='Faults', color='#ef4444', linewidth=2)
            plt.plot(hours, alarm_counts, marker='s', label='Alarms', color='#f59e0b', linewidth=2)
            
            plt.title('Hourly Distribution of Faults and Alarms', fontsize=14, fontweight='bold')
            plt.xlabel('Hour of Day', fontsize=12)
            plt.ylabel('Number of Events', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(hours)
            plt.tight_layout()
            
            # Dosyaya kaydet
            filename = f"hourly_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.reports_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"Error generating hourly distribution: {e}")
            return None
            
    def generate_summary_report(self, history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Özet rapor oluştur"""
        try:
            # Temel istatistikler
            total_events = len(history_data)
            faults = [e for e in history_data if e['type'] == 'fault']
            alarms = [e for e in history_data if e['type'] == 'alarm']
            
            # Bileşen analizi
            component_stats = defaultdict(lambda: {'faults': 0, 'alarms': 0})
            for entry in history_data:
                if entry['type'] in ['fault', 'alarm']:
                    component = entry['data'].get('component', 'Unknown')
                    if entry['type'] == 'fault':
                        component_stats[component]['faults'] += 1
                    else:
                        component_stats[component]['alarms'] += 1
                        
            # En problemli bileşen
            most_problematic = max(component_stats.items(), 
                                 key=lambda x: x[1]['faults'] + x[1]['alarms']) if component_stats else None
            
            # Günlük ortalama
            if history_data:
                first_date = datetime.fromisoformat(history_data[0]['timestamp']).date()
                last_date = datetime.fromisoformat(history_data[-1]['timestamp']).date()
                days = (last_date - first_date).days + 1
                daily_avg = total_events / days if days > 0 else 0
            else:
                daily_avg = 0
                
            # Son 24 saat
            last_24h = datetime.now() - timedelta(hours=24)
            recent_events = [
                e for e in history_data
                if datetime.fromisoformat(e['timestamp']) > last_24h
            ]
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_events': total_events,
                    'total_faults': len(faults),
                    'total_alarms': len(alarms),
                    'daily_average': round(daily_avg, 2),
                    'last_24h_events': len(recent_events)
                },
                'component_analysis': dict(component_stats),
                'most_problematic_component': most_problematic[0] if most_problematic else None,
                'recommendations': self._generate_recommendations(component_stats, most_problematic)
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating summary report: {e}")
            return {}
            
    def _generate_recommendations(self, component_stats: Dict, most_problematic: Optional[tuple]) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        if most_problematic:
            component, stats = most_problematic
            total_issues = stats['faults'] + stats['alarms']
            
            if total_issues > 10:
                recommendations.append(f"High priority: {component} component has {total_issues} issues")
            elif total_issues > 5:
                recommendations.append(f"Medium priority: {component} component needs attention")
                
        # Genel öneriler
        if len(component_stats) > 0:
            avg_issues = sum(s['faults'] + s['alarms'] for s in component_stats.values()) / len(component_stats)
            if avg_issues > 3:
                recommendations.append("Consider preventive maintenance schedule")
                
        if not recommendations:
            recommendations.append("System is operating normally")
            
        return recommendations
        
    def save_report(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Raporu dosyaya kaydet"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            print(f"Error saving report: {e}")
            return None
            
    def show_reporting_dialog(self, parent, history_data: List[Dict[str, Any]]):
        """Raporlama dialog'u göster"""
        dialog = tk.Toplevel(parent)
        dialog.title("Generate Reports")
        dialog.geometry("500x400")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Ana frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Generate Diagnostic Reports", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Rapor seçenekleri
        options_frame = ttk.LabelFrame(main_frame, text="Report Options", padding="10")
        options_frame.pack(fill="x", pady=(0, 20))
        
        # Fault trend
        fault_trend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Fault Trend Chart (7 days)", 
                       variable=fault_trend_var).pack(anchor="w")
        
        # Component analysis
        component_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Component Analysis Chart", 
                       variable=component_var).pack(anchor="w")
        
        # Hourly distribution
        hourly_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Hourly Distribution Chart", 
                       variable=hourly_var).pack(anchor="w")
        
        # Summary report
        summary_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Summary Report (JSON)", 
                       variable=summary_var).pack(anchor="w")
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        def generate_reports():
            generated_files = []
            
            try:
                if fault_trend_var.get():
                    filepath = self.generate_fault_trend_chart(history_data)
                    if filepath:
                        generated_files.append(filepath)
                        
                if component_var.get():
                    filepath = self.generate_component_analysis(history_data)
                    if filepath:
                        generated_files.append(filepath)
                        
                if hourly_var.get():
                    filepath = self.generate_hourly_distribution(history_data)
                    if filepath:
                        generated_files.append(filepath)
                        
                if summary_var.get():
                    report_data = self.generate_summary_report(history_data)
                    filepath = self.save_report(report_data)
                    if filepath:
                        generated_files.append(filepath)
                        
                if generated_files:
                    messagebox.showinfo("Success", 
                                      f"Generated {len(generated_files)} report(s) in {self.reports_dir}")
                else:
                    messagebox.showwarning("Warning", "No reports were generated")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate reports: {e}")
            finally:
                dialog.destroy()
                
        ttk.Button(button_frame, text="Generate Reports", 
                  command=generate_reports).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side="left")
        
        # Status
        status_label = ttk.Label(main_frame, text=f"Total history entries: {len(history_data)}")
        status_label.pack(pady=(20, 0))


# Global reporting instance
reporting = ReportingManager()
