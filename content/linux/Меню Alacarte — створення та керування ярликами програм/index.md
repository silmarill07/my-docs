---
title: "Меню Alacarte — створення та керування ярликами програм"
date: 2026-07-07
draft: false
tags: ["linux", "applications"]
image: "1.png"
description: "Огляд утиліти Alacarte для створення, редагування та видалення ярликів програм у меню застосунків Linux."
slug: "alacarte-menu-editor"
---

**Alacarte** — це графічна утиліта для керування меню програм у Linux. Вона дозволяє створювати власні ярлики, змінювати існуючі записи та приховувати непотрібні пункти меню без ручного редагування `.desktop`-файлів.

> [!NOTE]
> Alacarte працює з меню програм KDE, GNOME, але також може використовуватися в інших середовищах робочого столу, які підтримують стандарт **XDG Desktop Menu**.

## Основні можливості

* створення нових ярликів програм;
* редагування наявних записів;
* зміна назви, команди запуску, опису та значка;
* створення власних категорій меню;
* приховування або видалення непотрібних ярликів;
* швидке керування меню програм через графічний інтерфейс.

> [!TIP]
> Alacarte стане у пригоді, якщо потрібно створити ярлик для портативної програми, AppImage, власного скрипта або змінити параметри запуску вже встановленої програми.

## Коли варто використовувати

Alacarte буде корисною, якщо потрібно:

* додати власну програму до меню;
* змінити команду запуску застосунку;
* призначити власний значок;
* приховати непотрібні пункти меню;
* створити окрему категорію для власних програм або скриптів.

## Створіть файл зі скриптом

Наприклад:

```bash id="drw0n9"
nano Alacarte.pyw
```
Вставте наступний код:

``` bash
#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gtk, GdkPixbuf, GLib
import os
import subprocess
import shutil
import glob
import re

class DesktopEntryCreator(Gtk.Window):
    def __init__(self):
        super().__init__(title="Alacarte")
        self.set_border_width(10)
        self.set_default_size(700, 600)

        self.exec_path = ""
        self.icon_path = ""
        self.selected_system_icon = ""
        self.icon_mode = "system"  # "system" або "custom"
        self.desktop_dir = os.path.expanduser("~/.local/share/applications")
        self.categories = self.get_system_categories()
        self.system_icons = self.get_system_icons()

        # Створюємо notebook для перемикання між створенням та керуванням
        notebook = Gtk.Notebook()
        self.add(notebook)

        # Вкладка створення ярликів
        create_page = self.create_create_page()
        notebook.append_page(create_page, Gtk.Label(label="Створити ярлик"))

        # Вкладка керування ярликами
        manage_page = self.create_manage_page()
        notebook.append_page(manage_page, Gtk.Label(label="Керування ярликами"))

    def get_system_icons(self):
        """Отримуємо список системних іконок з усіх джерел"""
        icons = []
        processed_names = set()
        
        # 1. Отримуємо іконки з усіх доступних тем
        try:
            theme = Gtk.IconTheme.get_default()
            # Отримуємо всі доступні теми
            icon_list = theme.list_icons(None)
            for icon_name in icon_list[:200]:  # Обмежуємо кількість
                if icon_name not in processed_names:
                    icons.append((icon_name, icon_name))
                    processed_names.add(icon_name)
        except Exception as e:
            print(f"Помилка отримання іконок із теми: {e}")

        # 2. Шукаємо іконки в стандартних директоріях
        icon_dirs = [
            "/usr/share/icons",
            "/usr/share/pixmaps",
            os.path.expanduser("~/.local/share/icons"),
            os.path.expanduser("~/.icons")
        ]
        
        # Отримуємо всі піддиректорії з іконками
        all_icon_paths = []
        for base_dir in icon_dirs:
            if os.path.exists(base_dir):
                try:
                    # Рекурсивно шукаємо іконки у всіх піддиректоріях
                    for root, dirs, files in os.walk(base_dir):
                        for filename in files[:10]:  # Обмежуємо кількість файлів у кожній директорії
                            if filename.endswith(('.png', '.svg', '.xpm', '.ico', '.jpg', '.jpeg')):
                                icon_path = os.path.join(root, filename)
                                icon_name = os.path.splitext(filename)[0]
                                if icon_path not in [path for _, path in all_icon_paths]:
                                    all_icon_paths.append((icon_name, icon_path))
                except:
                    continue
        
        # Додаємо знайдені іконки
        for icon_name, icon_path in all_icon_paths[:100]:  # Обмежуємо загальну кількість
            if icon_name not in processed_names:
                icons.append((icon_name, icon_path))
                processed_names.add(icon_name)

        # 3. Отримуємо іконки з .desktop файлів
        desktop_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        
        for desktop_dir in desktop_dirs:
            if os.path.exists(desktop_dir):
                try:
                    for filename in os.listdir(desktop_dir)[:50]:  # Обмежуємо кількість
                        if filename.endswith('.desktop'):
                            filepath = os.path.join(desktop_dir, filename)
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    
                                    # Шукаємо Name= у файлі
                                    name_match = re.search(r'Name=([^\n]+)', content)
                                    icon_match = re.search(r'Icon=([^\n]+)', content)
                                    
                                    if name_match and icon_match:
                                        app_name = name_match.group(1).strip()
                                        icon_value = icon_match.group(1).strip()
                                        
                                        # Використовуємо назву додатка як ключ іконки
                                        if app_name not in processed_names:
                                            icons.append((app_name, icon_value))
                                            processed_names.add(app_name)
                            except:
                                continue
                except:
                    continue
        
        return icons[:300]  # Обмежуємо загальну кількість

    def get_system_categories(self):
        """Отримуємо список доступних категорій із системних .desktop файлів"""
        categories = set()
        system_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications"
        ]
        
        # Стандартні категорії
        standard_categories = [
            "AudioVideo", "Audio", "Video", "Development", "Education",
            "Game", "Graphics", "Network", "Office", "Science",
            "Settings", "System", "Utility"
        ]
        
        for category in standard_categories:
            categories.add(category)
        
        # Шукаємо категорії в системних файлах
        for system_dir in system_dirs:
            if os.path.exists(system_dir):
                try:
                    for filename in os.listdir(system_dir):
                        if filename.endswith('.desktop'):
                            filepath = os.path.join(system_dir, filename)
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    # Шукаємо Categories= у файлі
                                    match = re.search(r'Categories=([^;\n]+)', content)
                                    if match:
                                        cats = match.group(1).split(';')
                                        for cat in cats:
                                            if cat.strip():
                                                categories.add(cat.strip())
                            except:
                                continue
                except:
                    continue
        
        return sorted(list(categories))

    def create_create_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        
        # Executable
        self.exec_button = Gtk.Button(label="Вибрати виконуваний файл")
        self.exec_button.connect("clicked", self.on_exec_clicked)
        vbox.pack_start(self.exec_button, False, False, 20)

        self.exec_label = Gtk.Label(label="Файл не вибрано")
        self.exec_label.set_line_wrap(True)
        self.exec_label.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(self.exec_label, False, False, 0)

        # Вибір типу іконки
        icon_type_frame = Gtk.Frame(label="Вибір іконки")
        icon_type_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        icon_type_frame.add(icon_type_box)
        
        # Radio buttons для вибору типу іконки
        self.system_icon_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Вибрати системну іконку")
        self.custom_icon_radio = Gtk.RadioButton.new_with_label_from_widget(self.system_icon_radio, "Завантажити власну іконку")
        self.system_icon_radio.set_active(True)
        
        self.system_icon_radio.connect("toggled", self.on_icon_type_changed)
        self.custom_icon_radio.connect("toggled", self.on_icon_type_changed)
        
        icon_type_box.pack_start(self.system_icon_radio, False, False, 0)
        icon_type_box.pack_start(self.custom_icon_radio, False, False, 0)
        
        # Кнопка для вибору системних іконок
        self.system_icon_button = Gtk.Button(label="Вибрати системну іконку")
        self.system_icon_button.connect("clicked", self.on_system_icon_clicked)
        icon_type_box.pack_start(self.system_icon_button, False, False, 0)
        
        # Кнопка для завантаження своєї іконки
        self.custom_icon_button = Gtk.Button(label="Вибрати іконку з файлу")
        self.custom_icon_button.connect("clicked", self.on_custom_icon_clicked)
        self.custom_icon_button.set_sensitive(False)
        icon_type_box.pack_start(self.custom_icon_button, False, False, 0)

        vbox.pack_start(icon_type_frame, False, False, 0)

        # Відображення вибраної іконки
        self.icon_image = Gtk.Image()
        self.icon_image.set_size_request(64, 64)
        vbox.pack_start(self.icon_image, False, False, 5)
        
        # Label для відображення імені вибраної іконки
        self.icon_name_label = Gtk.Label(label="Іконку не вибрано")
        vbox.pack_start(self.icon_name_label, False, False, 0)

        # Name
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text("Назва додатка")
        self.name_entry.connect("changed", self.on_name_changed)
        vbox.pack_start(self.name_entry, False, False, 0)

        # Comment
        self.comment_entry = Gtk.Entry()
        self.comment_entry.set_placeholder_text("Опис додатка (опціонально)")
        vbox.pack_start(self.comment_entry, False, False, 0)

        # Category
        category_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        category_label = Gtk.Label(label="Категорія:")
        category_box.pack_start(category_label, False, False, 0)
        
        self.category_combo = Gtk.ComboBoxText()
        self.category_combo.append_text("Не вибрано")
        for category in self.categories:
            self.category_combo.append_text(category)
        self.category_combo.set_active(0)
        category_box.pack_start(self.category_combo, True, True, 0)
        
        vbox.pack_start(category_box, False, False, 0)

        # Terminal checkbox
        self.terminal_check = Gtk.CheckButton(label="Запускати в терміналі")
        vbox.pack_start(self.terminal_check, False, False, 0)

        # Create Button
        self.create_button = Gtk.Button(label="Створити ярлик")
        self.create_button.connect("clicked", self.on_create_clicked)
        vbox.pack_start(self.create_button, False, False, 10)

        return vbox

    def on_icon_type_changed(self, widget):
        """Обробник зміни типу іконки"""
        if self.system_icon_radio.get_active():
            self.icon_mode = "system"
            self.custom_icon_button.set_sensitive(False)
            self.system_icon_button.set_sensitive(True)
        else:
            self.icon_mode = "custom"
            self.custom_icon_button.set_sensitive(True)
            self.system_icon_button.set_sensitive(False)
        
        self.update_icon_preview()

    def update_icon_preview(self):
        """Оновлення прев'ю іконки"""
        try:
            if hasattr(self, 'selected_icon_info') and self.selected_icon_info:
                icon_name, icon_value = self.selected_icon_info
                
                # Намагаємося завантажити іконку кількома способами
                pixbuf = self.load_icon_by_value(icon_value)
                
                if pixbuf:
                    self.icon_image.set_from_pixbuf(pixbuf)
                    self.icon_name_label.set_text(f"Вибрано іконку: {icon_name}")
                else:
                    self.icon_image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
                    self.icon_name_label.set_text("Іконку не знайдено")
            else:
                self.icon_image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
                self.icon_name_label.set_text("Іконку не вибрано")
        except Exception as e:
            print(f"Помилка оновлення прев'ю іконки: {e}")
            self.icon_image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
            self.icon_name_label.set_text("Іконку не вибрано")

    def load_icon_by_value(self, icon_value):
        """Завантаження іконки за значенням (ім'я або шлях)"""
        try:
            # Якщо це шлях до файлу
            if os.path.exists(icon_value):
                return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    icon_value, 64, 64, True
                )
            
            # Якщо це ім'я іконки, намагаємося завантажити з теми
            theme = Gtk.IconTheme.get_default()
            try:
                return theme.load_icon(icon_value, 64, 0)
            except:
                # Пробуємо знайти іконку в стандартних директоріях
                icon_dirs = [
                    "/usr/share/icons",
                    "/usr/share/pixmaps",
                    os.path.expanduser("~/.local/share/icons"),
                    os.path.expanduser("~/.icons")
                ]
                
                for base_dir in icon_dirs:
                    if os.path.exists(base_dir):
                        for root, dirs, files in os.walk(base_dir):
                            for filename in files:
                                name_without_ext = os.path.splitext(filename)[0]
                                if name_without_ext == icon_value:
                                    icon_path = os.path.join(root, filename)
                                    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                                        icon_path, 64, 64, True
                                    )
        except:
            pass
        
        return None

    def on_system_icon_clicked(self, widget):
        """Відкриття діалогу вибору системної іконки"""
        dialog = Gtk.Dialog(title="Вибір системної іконки", parent=self, flags=0)
        dialog.set_default_size(700, 500)
        
        # Головний контейнер
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_border_width(10)
        
        # Поле пошуку
        search_entry = Gtk.Entry()
        search_entry.set_placeholder_text("Пошук іконок...")
        content_area.pack_start(search_entry, False, False, 0)
        
        # Створюємо сітку для іконок
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # Створюємо сітку іконок
        icon_grid = Gtk.FlowBox()
        icon_grid.set_valign(Gtk.Align.START)
        icon_grid.set_max_children_per_line(10)
        icon_grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
        icon_grid.set_homogeneous(True)
        icon_grid.set_min_children_per_line(5)
        icon_grid.set_row_spacing(8)
        icon_grid.set_column_spacing(8)
        
        # Зберігаємо всі іконки для пошуку (зберігати самі child елементи)
        self.all_icon_children = []  # (child, icon_name_lower)
        
        # Додаємо іконки в сітку
        for i, (icon_name, icon_value) in enumerate(self.system_icons):
            icon_box = self.create_icon_widget(icon_name, icon_value)
            if icon_box:
                child = Gtk.FlowBoxChild()
                child.add(icon_box)
                icon_grid.add(child)
                self.all_icon_children.append((child, icon_name.lower()))
                # Зберігаємо інформацію про іконку в child
                child.icon_info = (icon_name, icon_value)
        
        scrolled.add(icon_grid)
        content_area.pack_start(scrolled, True, True, 0)
        
        # Кнопки
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        dialog.show_all()
        
        # Таймер для debounce пошуку
        self.search_timer = None
        
        # Обробник пошуку
        def on_search_changed(entry):
            # Скасовуємо попередній таймер якщо є
            if self.search_timer:
                GLib.source_remove(self.search_timer)
            
            # Встановлюємо новий таймер (300ms debounce)
            self.search_timer = GLib.timeout_add(300, self.perform_search, 
                                               entry.get_text().lower(), icon_grid)
        
        search_entry.connect("changed", on_search_changed)
        
        # Обробник вибору іконки
        def on_icon_selected(flowbox, child):
            if hasattr(child, 'icon_info'):
                self.selected_icon_info = child.icon_info
                self.update_icon_preview()
        
        icon_grid.connect("child-activated", on_icon_selected)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_children = icon_grid.get_selected_children()
            if selected_children:
                child = selected_children[0]
                if hasattr(child, 'icon_info'):
                    self.selected_icon_info = child.icon_info
                    self.update_icon_preview()
        
        # Очищаємо таймер
        if self.search_timer:
            GLib.source_remove(self.search_timer)
            self.search_timer = None
            
        dialog.destroy()

    def perform_search(self, search_text, icon_grid):
        """Виконання пошуку іконок"""
        try:
            # Очищаємо сітку
            children = icon_grid.get_children()
            for child in children:
                icon_grid.remove(child)
            
            # Додаємо тільки підходящі іконки
            matching_children = []
            if search_text == "":
                # Якщо пустий пошук, показуємо всі іконки
                matching_children = self.all_icon_children
            else:
                # Інакше показуємо тільки ті, що збігаються
                for child, icon_name_lower in self.all_icon_children:
                    if search_text in icon_name_lower:
                        matching_children.append((child, icon_name_lower))
            
            # Додаємо підходящі іконки в сітку
            for child, icon_name_lower in matching_children:
                icon_grid.add(child)
                child.show_all()
            
            # Оновлюємо сітку
            icon_grid.show()
            
        except Exception as e:
            print(f"Помилка пошуку: {e}")
        
        # Скидаємо таймер
        self.search_timer = None
        return False  # Важливо: повертаємо False щоб видалити timeout callback

    def create_icon_widget(self, icon_name, icon_value):
        """Створення віджета для відображення іконки"""
        try:
            icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            icon_box.set_size_request(70, 70)
            
            # Іконка
            pixbuf = self.load_icon_by_value(icon_value)
            if pixbuf:
                # Масштабуємо іконку для відображення в сітці
                scaled_pixbuf = pixbuf.scale_simple(40, 40, GdkPixbuf.InterpType.BILINEAR)
                image = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
            else:
                image = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        except:
            image = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        
        icon_box.pack_start(image, False, False, 0)
        
        # Назва
        display_name = icon_name[:12] + "..." if len(icon_name) > 12 else icon_name
        label = Gtk.Label(label=display_name)
        label.set_max_width_chars(12)
        label.set_ellipsize(3)  # Pango.EllipsizeMode.END
        # Використовуємо CSS для зменшення шрифту
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"label { font-size: 9px; }")
        context = label.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        icon_box.pack_start(label, False, False, 0)
        
        return icon_box

    def on_custom_icon_clicked(self, widget):
        """Вибір користувацької іконки"""
        dialog = Gtk.FileChooserDialog(
            title="Виберіть іконку",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        # Встановлюємо початкову папку - папку виконуваного файлу
        if self.exec_path:
            exec_dir = os.path.dirname(self.exec_path)
            if os.path.exists(exec_dir):
                dialog.set_current_folder(exec_dir)

        filter_images = Gtk.FileFilter()
        filter_images.set_name("Зображення")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/svg+xml")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/x-icon")
        filter_images.add_mime_type("image/gif")
        dialog.add_filter(filter_images)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.icon_path = dialog.get_filename()
            # Для користувацької іконки зберігаємо інформацію
            icon_name = os.path.splitext(os.path.basename(self.icon_path))[0]
            self.selected_icon_info = (icon_name, self.icon_path)
            self.update_icon_preview()
        dialog.destroy()

    def on_name_changed(self, widget):
        """Автоматичний вибір іконки при зміні назви"""
        pass  # Поки вимкнено, оскільки вибір відбувається через UI

    def create_manage_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Заголовок
        label = Gtk.Label(label="Керування створеними ярликами")
        vbox.pack_start(label, False, False, 0)
        
        # Список ярликів
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # Створюємо список
        self.liststore = Gtk.ListStore(str, str, str, str, str)  # ім'я, шлях, іконка, коментар, категорія
        self.treeview = Gtk.TreeView(model=self.liststore)
        
        # Колонки
        renderer_text = Gtk.CellRendererText()
        column_name = Gtk.TreeViewColumn("Назва", renderer_text, text=0)
        self.treeview.append_column(column_name)
        
        column_comment = Gtk.TreeViewColumn("Опис", renderer_text, text=3)
        self.treeview.append_column(column_comment)
        
        column_category = Gtk.TreeViewColumn("Категорія", renderer_text, text=4)
        self.treeview.append_column(column_category)
        
        column_path = Gtk.TreeViewColumn("Шлях", renderer_text, text=1)
        self.treeview.append_column(column_path)
        
        scrolled.add(self.treeview)
        vbox.pack_start(scrolled, True, True, 0)
        
        # Кнопки керування
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.refresh_button = Gtk.Button(label="Оновити список")
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        button_box.pack_start(self.refresh_button, False, False, 0)
        
        self.delete_button = Gtk.Button(label="Видалити вибраний")
        self.delete_button.connect("clicked", self.on_delete_clicked)
        button_box.pack_start(self.delete_button, False, False, 0)
        
        vbox.pack_start(button_box, False, False, 0)
        
        # Завантажуємо список при першому відкритті
        self.load_desktop_entries()
        
        return vbox

    def on_exec_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Виберіть виконуваний файл",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.exec_path = dialog.get_filename()
            self.exec_label.set_text(self.exec_path)
        dialog.destroy()

    def on_create_clicked(self, widget):
        name = self.name_entry.get_text().strip()
        comment = self.comment_entry.get_text().strip()
        category_index = self.category_combo.get_active()
        category = None
        if category_index > 0:  # Якщо вибрано не "Не вибрано"
            category = self.category_combo.get_active_text()
        
        if not name or not self.exec_path:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="Будь ласка, вкажіть назву та виконуваний файл."
            )
            dialog.run()
            dialog.destroy()
            return

        # Визначаємо ім'я файлу ярлика
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
        if not safe_name:
            safe_name = "application"
        
        os.makedirs(self.desktop_dir, exist_ok=True)

        # Визначаємо іконку
        icon_value = "application-x-executable"  # значення за замовчуванням
        
        if hasattr(self, 'selected_icon_info') and self.selected_icon_info:
            icon_name, icon_source = self.selected_icon_info
            
            if self.icon_mode == "system":
                # Системна іконка - використовуємо початкове значення
                icon_value = icon_source
            elif self.icon_mode == "custom" and os.path.exists(icon_source):
                # Користувацька іконка - копіюємо та використовуємо шлях
                icon_ext = os.path.splitext(icon_source)[1]
                icon_target = os.path.join(self.desktop_dir, f"{safe_name}{icon_ext}")
                try:
                    shutil.copy(icon_source, icon_target)
                    icon_value = icon_target
                except Exception as e:
                    dialog_error = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Помилка копіювання іконки: {str(e)}"
                    )
                    dialog_error.run()
                    dialog_error.destroy()
                    return

        # Створюємо .desktop файл
        desktop_file_path = os.path.join(self.desktop_dir, f"{safe_name}.desktop")
        
        terminal = "true" if self.terminal_check.get_active() else "false"
        
        # Формуємо категорії
        categories_str = "Utility;"  # За замовчуванням
        if category:
            categories_str = f"{category};"
        
        desktop_content = f"""[Desktop Entry]
Name={name}
Comment={comment}
Exec={self.exec_path}
Icon={icon_value}
Terminal={terminal}
Type=Application
Categories={categories_str}
"""
        
        try:
            with open(desktop_file_path, 'w') as f:
                f.write(desktop_content)
            
            # Робимо файл виконуваним
            os.chmod(desktop_file_path, 0o755)
            
            self.refresh_applications()
            
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Ярлик успішно створено та додано!"
            )
            dialog.run()
            dialog.destroy()
            
            # Очищаємо поля
            self.clear_create_fields()
            
        except Exception as e:
            dialog_error = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Помилка створення ярлика: {str(e)}"
            )
            dialog_error.run()
            dialog_error.destroy()

    def clear_create_fields(self):
        """Очищаємо поля створення ярлика"""
        self.exec_path = ""
        self.icon_path = ""
        self.selected_system_icon = ""
        self.selected_icon_info = None
        self.icon_mode = "system"
        self.system_icon_radio.set_active(True)
        self.exec_label.set_text("Файл не вибрано")
        self.icon_image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        self.icon_name_label.set_text("Іконку не вибрано")
        self.name_entry.set_text("")
        self.comment_entry.set_text("")
        self.category_combo.set_active(0)
        self.terminal_check.set_active(False)

    def load_desktop_entries(self):
        """Завантажуємо список .desktop файлів"""
        self.liststore.clear()
        os.makedirs(self.desktop_dir, exist_ok=True)
        
        desktop_files = glob.glob(os.path.join(self.desktop_dir, "*.desktop"))
        
        for file_path in desktop_files:
            try:
                name = ""
                comment = ""
                icon_path = ""
                categories = ""
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if line.startswith("Name="):
                            name = line.strip().split("=", 1)[1]
                        elif line.startswith("Comment="):
                            comment = line.strip().split("=", 1)[1]
                        elif line.startswith("Icon="):
                            icon_path = line.strip().split("=", 1)[1]
                        elif line.startswith("Categories="):
                            categories = line.strip().split("=", 1)[1].rstrip(';')
                
                if name:
                    self.liststore.append([name, file_path, icon_path, comment, categories])
            except Exception:
                # Пропускаємо файли з помилками
                continue

    def on_refresh_clicked(self, widget):
        """Оновити список ярлыків"""
        # Оновлюємо список категорій
        self.categories = self.get_system_categories()
        self.category_combo.remove_all()
        self.category_combo.append_text("Не вибрано")
        for category in self.categories:
            self.category_combo.append_text(category)
        self.category_combo.set_active(0)
        
        # Оновлюємо список системних іконок
        self.system_icons = self.get_system_icons()
        
        self.load_desktop_entries()

    def on_delete_clicked(self, widget):
        """Видалити вибраний ярлик"""
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is None:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="Будь ласка, виберіть ярлик для видалення."
            )
            dialog.run()
            dialog.destroy()
            return
        
        name = model[treeiter][0]
        file_path = model[treeiter][1]
        icon_path = model[treeiter][2]
        
        # Підтвердження видалення
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Ви дійсно хочете видалити ярлик \"{name}\"?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            try:
                # Видаляємо .desktop файл
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Якщо іконка була скопійована в цю ж папку, видаляємо і її
                if icon_path and icon_path.startswith(self.desktop_dir) and os.path.exists(icon_path):
                    os.remove(icon_path)
                
                self.refresh_applications()
                self.load_desktop_entries()
                
                dialog_info = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Ярлик успішно видалено."
                )
                dialog_info.run()
                dialog_info.destroy()
                
            except Exception as e:
                dialog_error = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Помилка видалення ярлика: {str(e)}"
                )
                dialog_error.run()
                dialog_error.destroy()

    def refresh_applications(self):
        """Оновлення меню додатків системи"""
        try:
            # Намагаємося оновити кеш меню через стандартні утиліти
            subprocess.run(["update-desktop-database", self.desktop_dir], check=False)
        except:
            pass

if __name__ == "__main__":
    win = DesktopEntryCreator()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
```
## Зробіть файл виконуваним

```bash id="cvkqz7"
chmod +x Alacarte.pyw
```

> [!IMPORTANT]
> Alacarte змінює лише користувацькі записи меню і не впливає на системні файли, тому всі зміни можна легко скасувати.

## Підсумок

Alacarte — проста й зручна утиліта для керування ярликами програм у Linux. Вона дозволяє швидко створювати власні записи, редагувати параметри запуску та підтримувати меню програм у впорядкованому вигляді без ручного редагування `.desktop`-файлів.
