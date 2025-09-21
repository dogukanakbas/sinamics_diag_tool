"""
Authentication System - Kullanıcı kimlik doğrulama sistemi
"""
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import tkinter as tk
from tkinter import ttk, messagebox


class User:
    """Kullanıcı sınıfı"""
    
    def __init__(self, username: str, password_hash: str, role: str, 
                 full_name: str = "", email: str = "", is_active: bool = True):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.email = email
        self.is_active = is_active
        self.created_at = datetime.now()
        self.last_login = None
        self.login_attempts = 0
        self.locked_until = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Kullanıcıyı dictionary'ye çevir"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'full_name': self.full_name,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_attempts': self.login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Dictionary'den kullanıcı oluştur"""
        user = cls(
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            is_active=data.get('is_active', True)
        )
        user.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
        user.login_attempts = data.get('login_attempts', 0)
        if data.get('locked_until'):
            user.locked_until = datetime.fromisoformat(data['locked_until'])
        return user


class AuthenticationManager:
    """Kimlik doğrulama yöneticisi"""
    
    def __init__(self, users_file: str = "security/users.json"):
        self.users_file = users_file
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.session_timeout = timedelta(hours=8)
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        
        self._load_users()
        self._create_default_admin()
        
    def _load_users(self):
        """Kullanıcıları dosyadan yükle"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data.get('users', []):
                        user = User.from_dict(user_data)
                        self.users[user.username] = user
            except Exception as e:
                print(f"Error loading users: {e}")
                
    def _save_users(self):
        """Kullanıcıları dosyaya kaydet"""
        try:
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            data = {
                'users': [user.to_dict() for user in self.users.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving users: {e}")
            
    def _create_default_admin(self):
        """Varsayılan admin kullanıcısı oluştur"""
        if 'admin' not in self.users:
            admin_password = self._hash_password('admin123')
            admin_user = User(
                username='admin',
                password_hash=admin_password,
                role='admin',
                full_name='System Administrator',
                email='admin@company.com'
            )
            self.users['admin'] = admin_user
            self._save_users()
            
    def _hash_password(self, password: str) -> str:
        """Şifreyi hash'le"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _is_account_locked(self, user: User) -> bool:
        """Hesap kilitli mi kontrol et"""
        if user.locked_until and datetime.now() < user.locked_until:
            return True
        return False
        
    def _unlock_account(self, user: User):
        """Hesabı kilidi aç"""
        user.locked_until = None
        user.login_attempts = 0
        self._save_users()
        
    def login(self, username: str, password: str) -> bool:
        """Kullanıcı girişi"""
        if username not in self.users:
            return False
            
        user = self.users[username]
        
        # Hesap aktif mi?
        if not user.is_active:
            return False
            
        # Hesap kilitli mi?
        if self._is_account_locked(user):
            return False
            
        # Şifre doğru mu?
        password_hash = self._hash_password(password)
        if user.password_hash != password_hash:
            user.login_attempts += 1
            
            # Maksimum deneme sayısına ulaşıldı mı?
            if user.login_attempts >= self.max_login_attempts:
                user.locked_until = datetime.now() + self.lockout_duration
                
            self._save_users()
            return False
            
        # Başarılı giriş
        user.login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        self.current_user = user
        self._save_users()
        
        return True
        
    def logout(self):
        """Kullanıcı çıkışı"""
        self.current_user = None
        
    def is_logged_in(self) -> bool:
        """Kullanıcı giriş yapmış mı?"""
        if not self.current_user:
            return False
            
        # Session timeout kontrolü
        if self.current_user.last_login:
            if datetime.now() - self.current_user.last_login > self.session_timeout:
                self.logout()
                return False
                
        return True
        
    def has_permission(self, permission: str) -> bool:
        """Kullanıcının yetkisi var mı?"""
        if not self.is_logged_in():
            return False
            
        # Admin her şeyi yapabilir
        if self.current_user.role == 'admin':
            return True
            
        # Rol bazlı yetkiler
        role_permissions = {
            'operator': ['view_diagnostics', 'view_alarms'],
            'engineer': ['view_diagnostics', 'view_alarms', 'export_data', 'view_history'],
            'admin': ['*']  # Tüm yetkiler
        }
        
        user_permissions = role_permissions.get(self.current_user.role, [])
        return permission in user_permissions or '*' in user_permissions
        
    def get_current_user(self) -> Optional[User]:
        """Mevcut kullanıcıyı al"""
        return self.current_user if self.is_logged_in() else None
        
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str = "", email: str = "") -> bool:
        """Yeni kullanıcı oluştur"""
        if not self.has_permission('manage_users'):
            return False
            
        if username in self.users:
            return False
            
        password_hash = self._hash_password(password)
        user = User(username, password_hash, role, full_name, email)
        self.users[username] = user
        self._save_users()
        return True
        
    def update_user(self, username: str, **kwargs) -> bool:
        """Kullanıcı güncelle"""
        if not self.has_permission('manage_users'):
            return False
            
        if username not in self.users:
            return False
            
        user = self.users[username]
        
        # Güncellenebilir alanlar
        updatable_fields = ['role', 'full_name', 'email', 'is_active']
        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(user, field, value)
                
        self._save_users()
        return True
        
    def delete_user(self, username: str) -> bool:
        """Kullanıcı sil"""
        if not self.has_permission('manage_users'):
            return False
            
        if username == 'admin':  # Admin silinemez
            return False
            
        if username not in self.users:
            return False
            
        del self.users[username]
        self._save_users()
        return True
        
    def list_users(self) -> List[User]:
        """Kullanıcı listesi"""
        if not self.has_permission('manage_users'):
            return []
        return list(self.users.values())
        
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Şifre değiştir"""
        if username not in self.users:
            return False
            
        user = self.users[username]
        
        # Eski şifre doğru mu?
        if user.password_hash != self._hash_password(old_password):
            return False
            
        # Yeni şifreyi kaydet
        user.password_hash = self._hash_password(new_password)
        self._save_users()
        return True


class LoginWindow:
    """Giriş penceresi"""
    
    def __init__(self, parent, auth_manager: AuthenticationManager):
        self.parent = parent
        self.auth_manager = auth_manager
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Login - SINAMICS Diag & Viz")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Pencereyi ortala
        self.window.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Widget'ları oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="SINAMICS Diag & Viz", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Please login to continue", 
                                  font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # Giriş formu
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Kullanıcı adı
        ttk.Label(form_frame, text="Username:").pack(anchor="w")
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=30)
        username_entry.pack(fill="x", pady=(5, 15))
        
        # Şifre
        ttk.Label(form_frame, text="Password:").pack(anchor="w")
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                  show="*", width=30)
        password_entry.pack(fill="x", pady=(5, 15))
        
        # Giriş butonu
        login_button = ttk.Button(form_frame, text="Login", 
                                 command=self._login, width=20)
        login_button.pack(pady=(10, 0))
        
        # Hata mesajı
        self.error_label = ttk.Label(form_frame, text="", foreground="red")
        self.error_label.pack(pady=(10, 0))
        
        # Enter tuşu ile giriş
        self.window.bind('<Return>', lambda e: self._login())
        
        # İlk odak
        username_entry.focus()
        
    def _login(self):
        """Giriş işlemi"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.error_label.config(text="Please enter username and password")
            return
            
        if self.auth_manager.login(username, password):
            self.result = True
            self.window.destroy()
        else:
            user = self.auth_manager.users.get(username)
            if user and self.auth_manager._is_account_locked(user):
                self.error_label.config(text="Account is locked. Please try again later.")
            else:
                self.error_label.config(text="Invalid username or password")
                
    def show(self) -> bool:
        """Pencereyi göster ve sonucu döndür"""
        self.window.wait_window()
        return self.result is True


# Global auth manager
auth_manager = AuthenticationManager()
