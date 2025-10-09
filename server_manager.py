#!/usr/bin/env python3
"""
MkDocs Server Manager - Простое графическое приложение для управления сервером документации
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk, Gdk, GLib, Vte, Pango
import subprocess
import os
import webbrowser
import time
import socket

class ServerManager:
    def __init__(self):
        self.server_process = None
        self.venv_activated = False
        self.server_port = 8000
        self.server_url = f"http://localhost:{self.server_port}"
        
        # Создание главного окна
        self.window = Gtk.Window()
        self.window.set_title("MkDocs Server Manager")
        self.window.set_default_size(800, 600)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Подключение сигнала закрытия окна
        self.window.connect("delete-event", self.on_window_close)
        
        # Создание интерфейса
        self.create_ui()
        
        # Проверка состояния при запуске
        self.check_initial_state()
    
    def create_ui(self):
        """Создание пользовательского интерфейса"""
        # Главный контейнер
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_left(20)
        main_box.set_margin_right(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        self.window.add(main_box)
        
        # Заголовок
        title_label = Gtk.Label()
        title_label.set_markup("<span size='xx-large' weight='bold'>🚀 MkDocs Server Manager</span>")
        main_box.pack_start(title_label, False, False, 0)
        
        subtitle_label = Gtk.Label("Управление сервером документации")
        main_box.pack_start(subtitle_label, False, False, 0)
        
        # Панель управления
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        control_box.set_margin_top(20)
        control_box.set_margin_bottom(20)
        
        # Кнопка запуска
        self.start_button = Gtk.Button("▶️ Запустить сервер")
        self.start_button.set_size_request(150, 40)
        self.start_button.connect("clicked", self.on_start_server)
        
        # Кнопка остановки
        self.stop_button = Gtk.Button("⏹️ Остановить сервер")
        self.stop_button.set_size_request(150, 40)
        self.stop_button.connect("clicked", self.on_stop_server)
        self.stop_button.set_sensitive(False)
        
        # Статус сервера
        self.status_label = Gtk.Label("🔴 Сервер остановлен")
        
        # Кнопка открытия в браузере
        self.browser_button = Gtk.Button("🌐 Открыть в браузере")
        self.browser_button.connect("clicked", self.on_open_browser)
        self.browser_button.set_sensitive(False)
        
        control_box.pack_start(self.start_button, False, False, 0)
        control_box.pack_start(self.stop_button, False, False, 0)
        control_box.pack_start(self.status_label, False, False, 0)
        control_box.pack_end(self.browser_button, False, False, 0)
        
        main_box.pack_start(control_box, False, False, 0)
        
        # Терминал
        terminal_label = Gtk.Label("📟 Терминал")
        terminal_label.set_halign(Gtk.Align.START)
        main_box.pack_start(terminal_label, False, False, 0)
        
        # Создание VTE терминала
        self.terminal = Vte.Terminal()
        self.terminal.set_size(80, 24)
        self.terminal.set_font(Pango.FontDescription("Monospace 10"))
        
        # Настройка цветов терминала
        self.terminal.set_colors(
            Gdk.RGBA(0.9, 0.9, 0.9, 1.0),  # foreground
            Gdk.RGBA(0.1, 0.1, 0.1, 1.0),  # background
            []
        )
        
        # Скроллинг для терминала
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.terminal)
        scrolled_window.set_size_request(-1, 300)
        
        main_box.pack_start(scrolled_window, True, True, 0)
        
        # Запуск bash в терминале
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ["/bin/bash"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        
        self.window.show_all()
    
    def log_to_terminal(self, message):
        """Вывод сообщения в терминал"""
        command = f'echo "{message}"\n'
        self.terminal.feed_child(command.encode())
    
    def check_initial_state(self):
        """Проверка начального состояния"""
        self.log_to_terminal("🔍 Проверка состояния системы...")
        
        # Проверка виртуального окружения
        if os.path.exists('.venv'):
            self.log_to_terminal("✅ Виртуальное окружение найдено")
        else:
            self.log_to_terminal("❌ Виртуальное окружение не найдено")
        
        # Проверка порта
        if self.is_port_in_use(self.server_port):
            self.log_to_terminal(f"⚠️ Порт {self.server_port} уже используется")
        else:
            self.log_to_terminal(f"✅ Порт {self.server_port} свободен")
    
    def is_port_in_use(self, port):
        """Проверка, используется ли порт"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def kill_process_on_port(self, port):
        """Завершение процесса, использующего порт"""
        try:
            # Используем lsof для поиска процесса на порту
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        self.log_to_terminal(f"🔪 Завершение процесса PID: {pid}")
                        try:
                            os.kill(int(pid), 15)  # SIGTERM
                            time.sleep(1)
                        except ProcessLookupError:
                            pass
                return True
        except Exception as e:
            self.log_to_terminal(f"❌ Ошибка при завершении процесса: {e}")
        return False
    
    def check_venv_and_dependencies(self):
        """Проверка виртуального окружения и зависимостей"""
        venv_path = os.path.join(os.getcwd(), '.venv')
        
        # Проверяем, существует ли виртуальное окружение
        if not os.path.exists(venv_path):
            self.log_to_terminal("📦 Создание виртуального окружения...")
            self.terminal.feed_child(b'python3 -m venv .venv\n')
            time.sleep(3)
        
        # Проверяем, установлен ли mkdocs-material в виртуальном окружении
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        try:
            result = subprocess.run([pip_path, 'show', 'mkdocs-material'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.log_to_terminal("📥 Установка зависимостей в виртуальное окружение...")
                self.terminal.feed_child(b'source .venv/bin/activate && pip install -r requirements.txt\n')
                return False  # Нужно подождать установки
            else:
                self.log_to_terminal("✅ mkdocs-material уже установлен в виртуальном окружении")
                return True  # Можно сразу запускать сервер
                
        except Exception as e:
            self.log_to_terminal(f"⚠️ Ошибка проверки зависимостей: {e}")
            self.log_to_terminal("📥 Установка зависимостей...")
            self.terminal.feed_child(b'source .venv/bin/activate && pip install -r requirements.txt\n')
            return False
    
    def is_venv_activated(self):
        """Проверка, активировано ли виртуальное окружение"""
        return os.environ.get('VIRTUAL_ENV') is not None
    
    def on_start_server(self, button):
        """Обработчик запуска сервера"""
        self.log_to_terminal("🚀 Подготовка к запуску сервера...")
        
        # Проверка виртуального окружения и зависимостей
        if self.check_venv_and_dependencies():
            # Зависимости уже установлены, можно сразу запускать
            GLib.timeout_add(1000, self.continue_server_start)
        else:
            # Нужно подождать установки зависимостей
            GLib.timeout_add(8000, self.continue_server_start)
    
    def continue_server_start(self):
        """Продолжение запуска сервера после активации venv"""
        # Проверка и освобождение порта
        if self.is_port_in_use(self.server_port):
            self.log_to_terminal(f"⚠️ Порт {self.server_port} занят, освобождаем...")
            self.kill_process_on_port(self.server_port)
            time.sleep(1)
        
        # Активация виртуального окружения и запуск MkDocs сервера
        self.log_to_terminal("🌐 Запуск MkDocs сервера...")
        command = f'source .venv/bin/activate && mkdocs serve --dev-addr=localhost:{self.server_port}\n'
        self.terminal.feed_child(command.encode())
        
        # Обновление интерфейса
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self.browser_button.set_sensitive(True)
        
        self.status_label.set_text("🟢 Сервер запущен")
        
        # Проверка запуска сервера и открытие браузера
        GLib.timeout_add(3000, self.check_server_and_open_browser)
        
        return False  # Остановить таймер
    
    def check_server_and_open_browser(self):
        """Проверка запуска сервера и автоматическое открытие браузера"""
        if self.is_port_in_use(self.server_port):
            self.log_to_terminal("🌐 Сервер запущен, открываем браузер...")
            try:
                webbrowser.open(self.server_url)
                self.log_to_terminal(f"✅ Страница открыта: {self.server_url}")
            except Exception as e:
                self.log_to_terminal(f"❌ Ошибка открытия браузера: {e}")
        else:
            self.log_to_terminal("⚠️ Сервер еще не готов, ждем...")
            # Попробуем еще раз через секунду
            GLib.timeout_add(1000, self.check_server_and_open_browser)
        
        return False
    
    def on_stop_server(self, button):
        """Обработчик остановки сервера"""
        self.log_to_terminal("⏹️ Остановка сервера...")
        
        # Отправка Ctrl+C в терминал для остановки сервера
        self.terminal.feed_child(b'\x03')  # Ctrl+C
        
        # Обновление интерфейса
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self.browser_button.set_sensitive(False)
        
        self.status_label.set_text("🔴 Сервер остановлен")
        
        self.log_to_terminal("✅ Сервер остановлен")
    
    def on_open_browser(self, button):
        """Обработчик открытия браузера"""
        if not self.is_port_in_use(self.server_port):
            self.log_to_terminal("⚠️ Сервер не запущен или еще не готов")
            return
        
        try:
            webbrowser.open(self.server_url)
            self.log_to_terminal(f"🌐 Открыта страница: {self.server_url}")
        except Exception as e:
            self.log_to_terminal(f"❌ Ошибка открытия браузера: {e}")
            # Попробуем альтернативные способы
            try:
                subprocess.run(['xdg-open', self.server_url], check=True)
                self.log_to_terminal(f"✅ Страница открыта через xdg-open: {self.server_url}")
            except Exception as e2:
                self.log_to_terminal(f"❌ Ошибка xdg-open: {e2}")
    
    def on_window_close(self, window, event):
        """Обработчик закрытия окна"""
        if self.stop_button.get_sensitive():
            self.log_to_terminal("🛑 Остановка сервера перед закрытием...")
            self.terminal.feed_child(b'\x03')  # Ctrl+C
            time.sleep(1)
        
        Gtk.main_quit()
        return False

def main():
    """Главная функция"""
    app = ServerManager()
    Gtk.main()

if __name__ == "__main__":
    main()