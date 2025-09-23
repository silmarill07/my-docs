---
tags:
  - Linux
  - Gnome
---

# Перемикання мови у Gnome Wayland-сесії

!!! note "Ця інструкція дозволяє налаштувати перемикання розкладки клавіатури за допомогою Alt+Shift."

## Кроки налаштування

 - Відкрийте термінал та виконайте команду для перемикання розкладки через Alt+Shift:

```bash
gsettings set org.gnome.desktop.wm.keybindings switch-input-source-backward "['<Alt>Shift_L']"
```