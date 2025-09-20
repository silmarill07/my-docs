---
tags:
  - Linux
---

# Додаток для автозапуску програм

### Для роботи потрібно встановити:
```bash
sudo apt install python3 python3-gi
```
```bash
sudo apt install gir1.2-gtk-3.0
```
### Код програми
```bash
#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import os
import configparser

AUTOSTART_DIR = os.path.expanduser('~/.config/autostart')
APPLICATION_DIRS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications")
]

if not os.path.exists(AUTOSTART_DIR):
    os.makedirs(AUTOSTART_DIR)

class AutostartApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Автозапуск приложений")
        self.set_default_size(800, 400)

        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)

        self.liststore = Gtk.ListStore(str, str, int, bool)
        self.load_autostart_items()

        self.treeview = Gtk.TreeView(model=self.liststore)
        for i, column_title in enumerate(["Имя", "Команда запуска", "Таймаут (сек)"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        # Статус Вкл/Выкл
        renderer_status = Gtk.CellRendererText()
        column_status = Gtk.TreeViewColumn("Статус", renderer_status)
        column_status.set_cell_data_func(renderer_status, self.render_status)
        self.treeview.append_column(column_status)

        self.treeview.connect("button-press-event", self.on_treeview_right_click)
        vbox.pack_start(self.treeview, True, True, 0)

        # Кнопки снизу
        hbox = Gtk.HBox(spacing=6)
        vbox.pack_start(hbox, False, False, 0)

        btn_add = Gtk.Button(label="Добавить")
        btn_add.connect("clicked", self.on_add_clicked)
        hbox.pack_start(btn_add, True, True, 0)

    def render_status(self, column, cell, model, iter, data=None):
        enabled = model[iter][3]
        cell.set_property("text", "Вкл." if enabled else "Выкл.")

    def load_autostart_items(self):
        self.liststore.clear()
        for filename in os.listdir(AUTOSTART_DIR):
            if filename.endswith(".desktop"):
                path = os.path.join(AUTOSTART_DIR, filename)
                config = configparser.ConfigParser()
                config.read(path)

                if 'Desktop Entry' not in config:
                    continue
                entry = config['Desktop Entry']
                name = entry.get('Name', filename)
                exec_cmd = entry.get('Exec', '')
                enabled = entry.getboolean('X-GNOME-Autostart-enabled', fallback=True)
                timeout = 0

                if exec_cmd.startswith("bash -c 'sleep "):
                    try:
                        parts = exec_cmd.split('&&')
                        sleep_part = parts[0]
                        timeout = int(sleep_part.split()[3])
                        exec_cmd = parts[1].strip().strip("'")
                    except Exception:
                        timeout = 0
                self.liststore.append([name, exec_cmd, timeout, enabled])

    def on_add_clicked(self, widget):
        dialog = EditDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            name, command, timeout = dialog.get_data()
            self.add_autostart_item(name, command, timeout, enabled=True)
            self.load_autostart_items()

        dialog.destroy()

    def on_treeview_right_click(self, treeview, event):
        if event.button == 3:
            path_info = treeview.get_path_at_pos(int(event.x), int(event.y))
            if path_info is not None:
                path, column, cell_x, cell_y = path_info
                treeview.grab_focus()
                treeview.set_cursor(path, column, 0)

                model = treeview.get_model()
                treeiter = model.get_iter(path)
                if treeiter:
                    enabled = model[treeiter][3]
                    name = model[treeiter][0]

                    menu = Gtk.Menu()

                    item_edit = Gtk.MenuItem(label="Редактировать")
                    item_edit.connect("activate", self.on_edit_item, path)
                    menu.append(item_edit)

                    if enabled:
                        toggle_label = "Отключить"
                    else:
                        toggle_label = "Включить"
                    item_toggle = Gtk.MenuItem(label=toggle_label)
                    item_toggle.connect("activate", self.on_toggle_enabled, path, not enabled)
                    menu.append(item_toggle)

                    item_delete = Gtk.MenuItem(label="Удалить")
                    item_delete.connect("activate", self.on_delete_item, path)
                    menu.append(item_delete)

                    menu.show_all()
                    menu.popup_at_pointer(event)
            return True

    def on_edit_item(self, menuitem, path):
        iter = self.liststore.get_iter(path)
        if iter is not None:
            name, command, timeout, enabled = self.liststore[iter]
            dialog = EditDialog(self, name, command, timeout)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                new_name, new_command, new_timeout = dialog.get_data()
                self.remove_autostart_item(name)
                self.add_autostart_item(new_name, new_command, new_timeout, enabled)
                self.load_autostart_items()

            dialog.destroy()

    def on_toggle_enabled(self, menuitem, path, new_state):
        iter = self.liststore.get_iter(path)
        if iter is not None:
            name = self.liststore[iter][0]
            command = self.liststore[iter][1]
            timeout = self.liststore[iter][2]
            self.remove_autostart_item(name)
            self.add_autostart_item(name, command, timeout, new_state)
            self.load_autostart_items()

    def on_delete_item(self, menuitem, path):
        iter = self.liststore.get_iter(path)
        if iter is not None:
            name = self.liststore[iter][0]

            # Подтверждение удаления
            confirm = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"Удалить '{name}' из автозапуска?"
            )
            response = confirm.run()
            confirm.destroy()

            if response == Gtk.ResponseType.YES:
                self.remove_autostart_item(name)
                self.load_autostart_items()

    def add_autostart_item(self, name, command, timeout, enabled=True):
        filename = f"{name.replace(' ', '_')}.desktop"
        path = os.path.join(AUTOSTART_DIR, filename)
        exec_cmd = f"bash -c 'sleep {timeout} && {command}'" if timeout > 0 else command

        content = f"""[Desktop Entry]
Type=Application
Name={name}
Exec={exec_cmd}
X-GNOME-Autostart-enabled={'true' if enabled else 'false'}
NoDisplay=false
"""
        with open(path, 'w') as f:
            f.write(content)

    def remove_autostart_item(self, name):
        filename = f"{name.replace(' ', '_')}.desktop"
        path = os.path.join(AUTOSTART_DIR, filename)
        if os.path.exists(path):
            os.remove(path)

class EditDialog(Gtk.Dialog):
    def __init__(self, parent, name="", command="", timeout=0):
        Gtk.Dialog.__init__(self, title="Редактировать приложение", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_size(400, 200)

        box = self.get_content_area()
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        box.add(grid)

        self.entry_name = Gtk.Entry()
        self.entry_command = Gtk.Entry()
        self.entry_timeout = Gtk.Entry()

        self.entry_name.set_text(name)
        self.entry_command.set_text(command)
        self.entry_timeout.set_text(str(timeout))

        # Кнопка "Обзор" рядом с полем для имени приложения
        hbox_name = Gtk.HBox(spacing=6)
        grid.attach(Gtk.Label(label="Имя приложения:"), 0, 0, 1, 1)
        hbox_name.pack_start(self.entry_name, True, True, 0)

        btn_browse = Gtk.Button(label="Обзор...")
        btn_browse.connect("clicked", self.on_browse_clicked)
        hbox_name.pack_start(btn_browse, False, False, 0)

        grid.attach(hbox_name, 1, 0, 2, 1)

        grid.attach(Gtk.Label(label="Команда запуска:"), 0, 1, 1, 1)
        grid.attach(self.entry_command, 1, 1, 2, 1)

        grid.attach(Gtk.Label(label="Таймаут (сек):"), 0, 2, 1, 1)
        grid.attach(self.entry_timeout, 1, 2, 2, 1)

        self.show_all()

    def get_data(self):
        name = self.entry_name.get_text().strip()
        command = self.entry_command.get_text().strip()
        try:
            timeout = int(self.entry_timeout.get_text().strip())
            if timeout < 0:
                timeout = 0
        except ValueError:
            timeout = 0
        return name, command, timeout

    def on_browse_clicked(self, widget):
        dialog = Gtk.Dialog(title="Выберите приложение", transient_for=self, flags=0)
        dialog.set_default_size(500, 400)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        vbox = Gtk.VBox(spacing=6)
        box.pack_start(vbox, True, True, 0)

        search_entry = Gtk.Entry()
        search_entry.set_placeholder_text("Поиск...")
        vbox.pack_start(search_entry, False, False, 0)

        liststore = Gtk.ListStore(Gio.Icon, str, str)
        filterstore = liststore.filter_new()
        filterstore.set_visible_func(lambda model, iter, data: search_entry.get_text().lower() in model[iter][1].lower(), None)

        treeview = Gtk.TreeView(model=filterstore)
        icon_renderer = Gtk.CellRendererPixbuf()
        text_renderer = Gtk.CellRendererText()

        column = Gtk.TreeViewColumn("Приложение")
        column.pack_start(icon_renderer, False)
        column.pack_start(text_renderer, True)
        column.add_attribute(icon_renderer, "gicon", 0)
        column.add_attribute(text_renderer, "text", 1)

        treeview.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(treeview)
        vbox.pack_start(scroll, True, True, 0)

        def load_apps():
            liststore.clear()
            for app_dir in APPLICATION_DIRS:
                if os.path.isdir(app_dir):
                    for file in os.listdir(app_dir):
                        if file.endswith('.desktop'):
                            path = os.path.join(app_dir, file)
                            config = configparser.ConfigParser()
                            try:
                                config.read(path)
                                if 'Desktop Entry' in config:
                                    name = config['Desktop Entry'].get('Name')
                                    exec_cmd = config['Desktop Entry'].get('Exec')
                                    icon_name = config['Desktop Entry'].get('Icon')
                                    if name and exec_cmd:
                                        gicon = Gio.ThemedIcon.new(icon_name) if icon_name else None
                                        liststore.append([gicon, name, exec_cmd])
                            except Exception:
                                continue

        load_apps()

        search_entry.connect("changed", lambda e: filterstore.refilter())

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            model, treeiter = treeview.get_selection().get_selected()
            if treeiter is not None:
                name = model[treeiter][1]
                exec_cmd = model[treeiter][2]
                self.entry_name.set_text(name)
                self.entry_command.set_text(exec_cmd)

        dialog.destroy()

if __name__ == "__main__":
    win = AutostartApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
```