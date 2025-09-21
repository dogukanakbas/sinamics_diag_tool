"""
Export/Import System - Veri dışa/içe aktarma sistemi
"""
import json
import csv
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import tkinter as tk
from tkinter import filedialog, messagebox


class ExportImportManager:
    """Veri dışa/içe aktarma yöneticisi"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'xml']
        
    def export_diagnostics(self, data: Dict[str, Any], file_path: str, format: str = 'json') -> bool:
        """Teşhis verilerini dışa aktar"""
        try:
            if format.lower() == 'json':
                return self._export_json(data, file_path)
            elif format.lower() == 'csv':
                return self._export_csv(data, file_path)
            elif format.lower() == 'xml':
                return self._export_xml(data, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            print(f"Export error: {e}")
            return False
            
    def _export_json(self, data: Dict[str, Any], file_path: str) -> bool:
        """JSON formatında dışa aktar"""
        export_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'format': 'json',
                'version': '2.0'
            },
            'diagnostic_data': data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        return True
        
    def _export_csv(self, data: Dict[str, Any], file_path: str) -> bool:
        """CSV formatında dışa aktar"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Type', 'ID', 'Component', 'Description', 'Timestamp'])
            
            # Faults
            for fault in data.get('faults', []):
                writer.writerow([
                    'Fault',
                    fault.get('id', ''),
                    fault.get('component', ''),
                    fault.get('desc', ''),
                    datetime.now().isoformat()
                ])
                
            # Alarms
            for alarm in data.get('alarms', []):
                writer.writerow([
                    'Alarm',
                    alarm.get('id', ''),
                    alarm.get('component', ''),
                    alarm.get('desc', ''),
                    datetime.now().isoformat()
                ])
        return True
        
    def _export_xml(self, data: Dict[str, Any], file_path: str) -> bool:
        """XML formatında dışa aktar"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<diagnostic_data>\n'
        xml_content += f'  <export_info timestamp="{datetime.now().isoformat()}" format="xml" version="2.0"/>\n'
        
        # Faults
        xml_content += '  <faults>\n'
        for fault in data.get('faults', []):
            xml_content += f'    <fault id="{fault.get("id", "")}" component="{fault.get("component", "")}">\n'
            xml_content += f'      <description>{fault.get("desc", "")}</description>\n'
            xml_content += '    </fault>\n'
        xml_content += '  </faults>\n'
        
        # Alarms
        xml_content += '  <alarms>\n'
        for alarm in data.get('alarms', []):
            xml_content += f'    <alarm id="{alarm.get("id", "")}" component="{alarm.get("component", "")}">\n'
            xml_content += f'      <description>{alarm.get("desc", "")}</description>\n'
            xml_content += '    </alarm>\n'
        xml_content += '  </alarms>\n'
        
        xml_content += '</diagnostic_data>\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        return True
        
    def import_diagnostics(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Teşhis verilerini içe aktar"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.json':
                return self._import_json(file_path)
            elif file_ext == '.csv':
                return self._import_csv(file_path)
            elif file_ext == '.xml':
                return self._import_xml(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            print(f"Import error: {e}")
            return None
            
    def _import_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """JSON formatından içe aktar"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Eski format uyumluluğu
        if 'diagnostic_data' in data:
            return data['diagnostic_data']
        else:
            return data
            
    def _import_csv(self, file_path: str) -> Optional[Dict[str, Any]]:
        """CSV formatından içe aktar"""
        faults = []
        alarms = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = {
                    'id': row.get('ID', ''),
                    'component': row.get('Component', ''),
                    'desc': row.get('Description', '')
                }
                
                if row.get('Type', '').lower() == 'fault':
                    faults.append(item)
                elif row.get('Type', '').lower() == 'alarm':
                    alarms.append(item)
                    
        return {'faults': faults, 'alarms': alarms}
        
    def _import_xml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """XML formatından içe aktar"""
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        faults = []
        alarms = []
        
        # Faults
        for fault in root.findall('.//fault'):
            faults.append({
                'id': fault.get('id', ''),
                'component': fault.get('component', ''),
                'desc': fault.find('description').text if fault.find('description') is not None else ''
            })
            
        # Alarms
        for alarm in root.findall('.//alarm'):
            alarms.append({
                'id': alarm.get('id', ''),
                'component': alarm.get('component', ''),
                'desc': alarm.find('description').text if alarm.find('description') is not None else ''
            })
            
        return {'faults': faults, 'alarms': alarms}
        
    def export_history(self, history_data: List[Dict[str, Any]], file_path: str, format: str = 'json') -> bool:
        """Geçmiş verilerini dışa aktar"""
        try:
            if format.lower() == 'json':
                return self._export_json(history_data, file_path)
            elif format.lower() == 'csv':
                return self._export_history_csv(history_data, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            print(f"History export error: {e}")
            return False
            
    def _export_history_csv(self, history_data: List[Dict[str, Any]], file_path: str) -> bool:
        """Geçmiş verilerini CSV formatında dışa aktar"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Timestamp', 'Type', 'Description', 'Data'])
            
            # Data
            for entry in history_data:
                writer.writerow([
                    entry.get('timestamp', ''),
                    entry.get('type', ''),
                    entry.get('description', ''),
                    json.dumps(entry.get('data', {}))
                ])
        return True
        
    def show_export_dialog(self, parent, data: Dict[str, Any]) -> Optional[str]:
        """Dışa aktarma dialog'u göster"""
        file_path = filedialog.asksaveasfilename(
            parent=parent,
            title="Export Diagnostic Data",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            format = os.path.splitext(file_path)[1][1:].lower()
            if self.export_diagnostics(data, file_path, format):
                messagebox.showinfo("Export", f"Data exported successfully to {file_path}")
                return file_path
            else:
                messagebox.showerror("Export Error", "Failed to export data")
        return None
        
    def show_import_dialog(self, parent) -> Optional[Dict[str, Any]]:
        """İçe aktarma dialog'u göster"""
        file_path = filedialog.askopenfilename(
            parent=parent,
            title="Import Diagnostic Data",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            data = self.import_diagnostics(file_path)
            if data:
                messagebox.showinfo("Import", f"Data imported successfully from {file_path}")
                return data
            else:
                messagebox.showerror("Import Error", "Failed to import data")
        return None
        
    def get_export_summary(self, data: Dict[str, Any]) -> str:
        """Dışa aktarma özeti"""
        fault_count = len(data.get('faults', []))
        alarm_count = len(data.get('alarms', []))
        
        return f"Export Summary:\n" \
               f"- Faults: {fault_count}\n" \
               f"- Alarms: {alarm_count}\n" \
               f"- Total: {fault_count + alarm_count}\n" \
               f"- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# Global export/import instance
export_import = ExportImportManager()
