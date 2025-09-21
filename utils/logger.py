"""
Logging System - Hata ve olay kaydetme sistemi
"""
import logging
import os
from datetime import datetime
from typing import Optional


class DiagnosticLogger:
    """Teşhis uygulaması için özel logger"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
        self._setup_loggers()
        
    def _ensure_log_dir(self):
        """Log klasörünü oluştur"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def _setup_loggers(self):
        """Logger'ları ayarla"""
        # Ana logger
        self.main_logger = logging.getLogger('sinamics_diag')
        self.main_logger.setLevel(logging.INFO)
        
        # Dosya handler
        log_file = os.path.join(self.log_dir, f"sinamics_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Handler'ları ekle
        if not self.main_logger.handlers:
            self.main_logger.addHandler(file_handler)
            self.main_logger.addHandler(console_handler)
            
        # Hata logger
        self.error_logger = logging.getLogger('sinamics_diag.errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_file = os.path.join(self.log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setFormatter(formatter)
        
        if not self.error_logger.handlers:
            self.error_logger.addHandler(error_handler)
            
        # Teşhis logger
        self.diag_logger = logging.getLogger('sinamics_diag.diagnostics')
        self.diag_logger.setLevel(logging.INFO)
        
        diag_file = os.path.join(self.log_dir, f"diagnostics_{datetime.now().strftime('%Y%m%d')}.log")
        diag_handler = logging.FileHandler(diag_file, encoding='utf-8')
        diag_handler.setFormatter(formatter)
        
        if not self.diag_logger.handlers:
            self.diag_logger.addHandler(diag_handler)
    
    def info(self, message: str):
        """Bilgi mesajı logla"""
        self.main_logger.info(message)
        
    def warning(self, message: str):
        """Uyarı mesajı logla"""
        self.main_logger.warning(message)
        
    def error(self, message: str, exception: Optional[Exception] = None):
        """Hata mesajı logla"""
        if exception:
            self.error_logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.error_logger.error(message)
        self.main_logger.error(message)
        
    def log_diagnostic(self, diagnostic_data: dict):
        """Teşhis verisini logla"""
        self.diag_logger.info(f"Diagnostic data: {diagnostic_data}")
        
    def log_connection_event(self, event: str, details: str = ""):
        """Bağlantı olayını logla"""
        self.main_logger.info(f"Connection event: {event} - {details}")
        
    def log_user_action(self, action: str, details: str = ""):
        """Kullanıcı aksiyonunu logla"""
        self.main_logger.info(f"User action: {action} - {details}")
        
    def get_log_files(self) -> list:
        """Log dosyalarını listele"""
        if not os.path.exists(self.log_dir):
            return []
        return [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
        
    def clear_old_logs(self, days: int = 30):
        """Eski log dosyalarını temizle"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        for filename in self.get_log_files():
            file_path = os.path.join(self.log_dir, filename)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    self.info(f"Removed old log file: {filename}")
                except Exception as e:
                    self.error(f"Failed to remove log file {filename}", e)


# Global logger instance
logger = DiagnosticLogger()
