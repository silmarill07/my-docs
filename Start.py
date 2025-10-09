#!/usr/bin/env python3
"""
MkDocs Server Manager - Простое приложение для управления сервером
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk, GLib, Vte, Pango
import subprocess
import os
import webbrowser
import time
import socket

class MkDocsManager:
    def __init__(self):
        self.server_port = 8000
        self.server_url = f"http://localhost:{self.server_port}"
        
        # Создание окна
        self.window = Gtk.Window()
        self.window.set_title("MkDocs Server Manager")
        self.window.set_default_size(800, 600)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete-event", self.on_close)
        
        self.create_ui()
        self.check_environment()
    
    def create_ui(self):
        """Создание интерфейса"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_left(20)
        vbox.set_margin_right(20)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        
        # Заголовок
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>🚀 MkDocs Manager</span>")
        vbox.pack_start(title, False, False, 0)
        
        # Кнопки управления
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_top(20)
        
        self.start_btn = Gtk.Button("▶️ Запустить")
        self.start_btn.connect("clicked", self.start_server)
        self.start_btn.set_size_request(120, 40)
        
        self.stop_btn = Gtk.Button("⏹️ Остановить")
        self.stop_btn.connect("clicked", self.stop_server)
        self.stop_btn.set_sensitive(False)
        self.stop_btn.set_size_request(120, 40)
        
        self.browser_btn = Gtk.Button("🌐 Браузер")
        self.browser_btn.connect("clicked", self.open_browser)
        self.browser_btn.set_sensitive(False)
        
        self.status_label = Gtk.Label("🔴 Остановлен")
        
        hbox.pack_start(self.start_btn, False, False, 0)
        hbox.pack_start(self.stop_btn, False, False, 0)
        hbox.pack_start(self.browser_btn, False, False, 0)
        hbox.pack_end(self.status_label, False, False, 0)
        
        vbox.pack_start(hbox, False, False, 0)
        
        # Терминал
        terminal_label = Gtk.Label("📟 Терминал:")
        terminal_label.set_halign(Gtk.Align.START)
        vbox.pack_start(terminal_label, False, False, 0)
        
        self.terminal = Vte.Terminal()
        self.terminal.set_font(Pango.FontDescription("Monospace 10"))
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.terminal)
        scrolled.set_size_request(-1, 350)
        vbox.pack_start(scrolled, True, True, 0)
        
        self.window.add(vbox)
        
        # Запуск bash в терминале
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.getcwd(),
            ["/bin/bash"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        
        self.window.show_all()
    
    def log(self, message):
        """Вывод в терминал"""
        self.terminal.feed_child(f'echo "{message}"\n'.encode())
    
    def check_environment(self):
        """Проверка окружения"""
        self.log("🔍 Проверка окружения...")
        
        # Проверка системных зависимостей
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            gi.require_version('Vte', '2.91')
            self.log("✅ GTK и VTE доступны")
        except Exception as e:
            self.log("❌ Системные зависимости не установлены!")
            self.log("Установите: sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-vte-2.91")
            return
        
        if not os.path.exists('mkdocs.yml'):
            self.log("❌ mkdocs.yml не найден!")
            return
        
        if os.path.exists('.venv'):
            self.log("✅ Виртуальное окружение найдено")
        else:
            self.log("⚠️ Виртуальное окружение не найдено, будет создано")
        
        if self.is_port_busy():
            self.log(f"⚠️ Порт {self.server_port} занят")
        else:
            self.log(f"✅ Порт {self.server_port} свободен")
    
    def is_port_busy(self):
        """Проверка порта"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', self.server_port)) == 0
        except:
            return False
    
    def check_mkdocs_installed(self):
        """Проверка установки mkdocs-material в venv"""
        try:
            pip_path = os.path.join('.venv', 'bin', 'pip')
            if os.path.exists(pip_path):
                result = subprocess.run([pip_path, 'show', 'mkdocs-material'], 
                                      capture_output=True, text=True, timeout=10)
                return result.returncode == 0
        except:
            pass
        return False
    
    def setup_venv(self):
        """Настройка виртуального окружения"""
        if not os.path.exists('.venv'):
            self.log("📦 Создание виртуального окружения...")
            self.terminal.feed_child(b'python3 -m venv .venv\n')
            time.sleep(2)
            need_install = True
        else:
            need_install = not self.check_mkdocs_installed()
        
        self.log("🔄 Активация виртуального окружения...")
        self.terminal.feed_child(b'source .venv/bin/activate\n')
        time.sleep(1)
        
        if need_install:
            self.log("📥 Установка зависимостей...")
            self.terminal.feed_child(b'pip install -r requirements.txt\n')
        else:
            self.log("✅ mkdocs-material уже установлен, пропускаем установку")
    
    def start_server(self, button):
        """Запуск сервера"""
        self.log("🚀 Запуск сервера...")
        
        # Освобождение порта если занят
        if self.is_port_busy():
            self.log("🔪 Освобождение порта...")
            try:
                subprocess.run(['pkill', '-f', 'mkdocs'], timeout=5)
                time.sleep(1)
            except:
                pass
        
        # Настройка окружения
        self.setup_venv()
        
        # Запуск через несколько секунд
        GLib.timeout_add(5000, self.actually_start_server)
        
        # Обновление интерфейса
        self.start_btn.set_sensitive(False)
        self.status_label.set_text("🟡 Подготовка...")
    
    def actually_start_server(self):
        """Фактический запуск сервера"""
        self.log("🌐 Запуск MkDocs сервера...")
        
        # Активация venv и запуск
        self.terminal.feed_child(b'source .venv/bin/activate\n')
        time.sleep(1)
        command = f'mkdocs serve --dev-addr=localhost:{self.server_port}\n'
        self.terminal.feed_child(command.encode())
        
        # Обновление интерфейса
        self.stop_btn.set_sensitive(True)
        self.browser_btn.set_sensitive(True)
        self.status_label.set_text("🟢 Запущен")
        
        # Открытие браузера через 3 секунды
        GLib.timeout_add(3000, self.auto_open_browser)
        
        return False
    
    def auto_open_browser(self):
        """Автоматическое открытие браузера"""
        if self.is_port_busy():
            self.log("🌐 Автоматическое открытие браузера...")
            
            # Пробуем разные способы
            methods = [
                ('webbrowser', lambda: webbrowser.open(self.server_url)),
                ('xdg-open', lambda: subprocess.run(['xdg-open', self.server_url], check=True, timeout=5)),
                ('firefox', lambda: subprocess.run(['firefox', self.server_url], check=True, timeout=5)),
                ('google-chrome', lambda: subprocess.run(['google-chrome', self.server_url], check=True, timeout=5))
            ]
            
            for method_name, method_func in methods:
                try:
                    method_func()
                    self.log(f"✅ Браузер открыт через {method_name}: {self.server_url}")
                    return False
                except Exception as e:
                    continue
            
            self.log(f"⚠️ Автоматическое открытие не удалось. URL: {self.server_url}")
        else:
            # Попробуем еще раз через секунду (максимум 10 попыток)
            if not hasattr(self, 'browser_attempts'):
                self.browser_attempts = 0
            
            self.browser_attempts += 1
            if self.browser_attempts < 10:
                self.log(f"⏳ Ждем запуска сервера... (попытка {self.browser_attempts}/10)")
                GLib.timeout_add(1000, self.auto_open_browser)
            else:
                self.log("⚠️ Сервер не запустился за 10 секунд")
        
        return False
    
    def stop_server(self, button):
        """Остановка сервера"""
        self.log("⏹️ Остановка сервера...")
        
        # Отправка Ctrl+C
        self.terminal.feed_child(b'\x03')
        
        # Обновление интерфейса
        self.start_btn.set_sensitive(True)
        self.stop_btn.set_sensitive(False)
        self.browser_btn.set_sensitive(False)
        self.status_label.set_text("🔴 Остановлен")
        
        self.log("✅ Сервер остановлен")
    
    def open_browser(self, button):
        """Открытие браузера"""
        if not self.is_port_busy():
            self.log("⚠️ Сервер не запущен")
            return
        
        self.log(f"🌐 Попытка открыть: {self.server_url}")
        
        # Способ 1: webbrowser
        try:
            webbrowser.open(self.server_url)
            self.log("✅ Браузер открыт через webbrowser")
            return
        except Exception as e:
            self.log(f"⚠️ webbrowser не сработал: {e}")
        
        # Способ 2: xdg-open
        try:
            subprocess.run(['xdg-open', self.server_url], check=True, timeout=5)
            self.log("✅ Браузер открыт через xdg-open")
            return
        except Exception as e:
            self.log(f"⚠️ xdg-open не сработал: {e}")
        
        # Способ 3: firefox
        try:
            subprocess.run(['firefox', self.server_url], check=True, timeout=5)
            self.log("✅ Браузер открыт через firefox")
            return
        except Exception as e:
            self.log(f"⚠️ firefox не сработал: {e}")
        
        # Способ 4: google-chrome
        try:
            subprocess.run(['google-chrome', self.server_url], check=True, timeout=5)
            self.log("✅ Браузер открыт через google-chrome")
            return
        except Exception as e:
            self.log(f"⚠️ google-chrome не сработал: {e}")
        
        self.log(f"❌ Не удалось открыть браузер. Откройте вручную: {self.server_url}")
    
    def on_close(self, window, event):
        """Закрытие окна"""
        if self.stop_btn.get_sensitive():
            self.log("🛑 Остановка сервера...")
            self.terminal.feed_child(b'\x03')
            time.sleep(1)
        
        Gtk.main_quit()
        return False

def main():
    app = MkDocsManager()
    Gtk.main()

if __name__ == "__main__":
    main()