---
tags:
  - Linux
---

# Автоматичне монтування HDD

!!! tip "Підказка"
    Перед початком дізнайтесь UUID вашого диска за допомогою команди `blkid`.

## Кроки налаштування

### 1. Створити точку монтування:
```bash
sudo mkdir -p /mnt/hdd
```

### 2. Відредагувати `fstab`:
```bash
sudo nano /etc/fstab
```

### 3. Додати рядок у кінець файлу:
```text
UUID=6A0CED7D0CED44A3  /mnt/hdd  ntfs-3g  defaults,nofail,x-systemd.device-timeout=10  0  0
```

### 4. Перезапустити конфігурацію systemd:
```bash
sudo systemctl daemon-reload
```

### 5. Перемонтувати всі файлові системи:
```bash
sudo mount -a
```

### 6. Перевірити доступність диска:
```bash
ls /mnt/hdd
```