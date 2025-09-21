"""
History Management System - Alarm/fault geçmişi yönetimi
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque


class HistoryManager:
    """Teşhis geçmişi yöneticisi"""
    
    def __init__(self, max_entries: int = 1000, save_interval: int = 60):
        self.max_entries = max_entries
        self.save_interval = save_interval
        self.history_file = "history.json"
        self.history = deque(maxlen=max_entries)
        self.last_save = datetime.now()
        self._load_history()
        
    def _load_history(self):
        """Geçmişi dosyadan yükle"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry in data.get('entries', []):
                        self.history.append(entry)
            except Exception as e:
                print(f"History load error: {e}")
                
    def _save_history(self):
        """Geçmişi dosyaya kaydet"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_entries': len(self.history),
                'entries': list(self.history)
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.last_save = datetime.now()
        except Exception as e:
            print(f"History save error: {e}")
            
    def add_entry(self, entry_type: str, data: Dict[str, Any], description: str = ""):
        """Geçmişe yeni kayıt ekle"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': entry_type,  # 'fault', 'alarm', 'clear', 'connection', 'user_action'
            'data': data,
            'description': description
        }
        
        self.history.append(entry)
        
        # Belirli aralıklarla kaydet
        if (datetime.now() - self.last_save).seconds >= self.save_interval:
            self._save_history()
            
    def add_fault(self, fault_data: Dict[str, Any]):
        """Fault kaydı ekle"""
        self.add_entry('fault', fault_data, f"Fault detected: {fault_data.get('id', 'Unknown')}")
        
    def add_alarm(self, alarm_data: Dict[str, Any]):
        """Alarm kaydı ekle"""
        self.add_entry('alarm', alarm_data, f"Alarm detected: {alarm_data.get('id', 'Unknown')}")
        
    def add_clear_event(self, cleared_items: List[str]):
        """Temizleme olayı ekle"""
        self.add_entry('clear', {'cleared_items': cleared_items}, f"Cleared: {', '.join(cleared_items)}")
        
    def add_connection_event(self, event_type: str, details: str = ""):
        """Bağlantı olayı ekle"""
        self.add_entry('connection', {'event': event_type, 'details': details}, f"Connection: {event_type}")
        
    def add_user_action(self, action: str, details: str = ""):
        """Kullanıcı aksiyonu ekle"""
        self.add_entry('user_action', {'action': action, 'details': details}, f"User: {action}")
        
    def get_recent_entries(self, count: int = 50) -> List[Dict[str, Any]]:
        """Son kayıtları al"""
        return list(self.history)[-count:]
        
    def get_entries_by_type(self, entry_type: str) -> List[Dict[str, Any]]:
        """Belirli tipte kayıtları al"""
        return [entry for entry in self.history if entry['type'] == entry_type]
        
    def get_entries_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Tarih aralığındaki kayıtları al"""
        result = []
        for entry in self.history:
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if start_date <= entry_date <= end_date:
                result.append(entry)
        return result
        
    def get_fault_statistics(self) -> Dict[str, Any]:
        """Fault istatistikleri"""
        faults = self.get_entries_by_type('fault')
        if not faults:
            return {'total': 0, 'by_component': {}, 'by_id': {}}
            
        stats = {
            'total': len(faults),
            'by_component': {},
            'by_id': {}
        }
        
        for fault in faults:
            fault_data = fault['data']
            component = fault_data.get('component', 'Unknown')
            fault_id = fault_data.get('id', 'Unknown')
            
            stats['by_component'][component] = stats['by_component'].get(component, 0) + 1
            stats['by_id'][fault_id] = stats['by_id'].get(fault_id, 0) + 1
            
        return stats
        
    def get_alarm_statistics(self) -> Dict[str, Any]:
        """Alarm istatistikleri"""
        alarms = self.get_entries_by_type('alarm')
        if not alarms:
            return {'total': 0, 'by_component': {}, 'by_id': {}}
            
        stats = {
            'total': len(alarms),
            'by_component': {},
            'by_id': {}
        }
        
        for alarm in alarms:
            alarm_data = alarm['data']
            component = alarm_data.get('component', 'Unknown')
            alarm_id = alarm_data.get('id', 'Unknown')
            
            stats['by_component'][component] = stats['by_component'].get(component, 0) + 1
            stats['by_id'][alarm_id] = stats['by_id'].get(alarm_id, 0) + 1
            
        return stats
        
    def get_daily_summary(self, date: datetime) -> Dict[str, Any]:
        """Günlük özet"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        day_entries = self.get_entries_by_date_range(start_of_day, end_of_day)
        
        summary = {
            'date': date.strftime('%Y-%m-%d'),
            'total_events': len(day_entries),
            'faults': len([e for e in day_entries if e['type'] == 'fault']),
            'alarms': len([e for e in day_entries if e['type'] == 'alarm']),
            'clear_events': len([e for e in day_entries if e['type'] == 'clear']),
            'connection_events': len([e for e in day_entries if e['type'] == 'connection']),
            'user_actions': len([e for e in day_entries if e['type'] == 'user_action'])
        }
        
        return summary
        
    def export_history(self, file_path: str, format: str = 'json') -> bool:
        """Geçmişi dışa aktar"""
        try:
            if format.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(list(self.history), f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if self.history:
                        writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'description', 'data'])
                        writer.writeheader()
                        for entry in self.history:
                            row = {
                                'timestamp': entry['timestamp'],
                                'type': entry['type'],
                                'description': entry['description'],
                                'data': json.dumps(entry['data'])
                            }
                            writer.writerow(row)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
            
    def clear_history(self):
        """Geçmişi temizle"""
        self.history.clear()
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
            
    def cleanup_old_entries(self, days: int = 30):
        """Eski kayıtları temizle"""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.history = deque(
            [entry for entry in self.history 
             if datetime.fromisoformat(entry['timestamp']) > cutoff_date],
            maxlen=self.max_entries
        )
        
    def force_save(self):
        """Zorla kaydet"""
        self._save_history()


# Global history instance
history = HistoryManager()
