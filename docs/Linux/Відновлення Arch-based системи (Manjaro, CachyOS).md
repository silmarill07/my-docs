---
tags:
  - Linux
  - Manjaro (Arch)
---

# Відновлення Arch-based системи (Manjaro, CachyOS)

!!! info "Навіщо це потрібно?"
    Це покрокове керівництво допоможе діагностувати та відновити систему на базі Arch у випадку проблем із завантаженням чи роботою.

---

## 🔧 Крок 1. Визнач рівень поломки

### Випадок A: система частково завантажується
- Чорний екран із курсором  
- Мерехтливий курсор  
- Зависання при завантаженні  
- Доступний `Ctrl + Alt + F2`  

### Випадок B: система взагалі не стартує
- Чорний екран одразу  
- Kernel panic  
- Немає меню GRUB  
- Система не реагує  

---

## 🚀 Випадок A: Система частково завантажується

1. Перемкнись у термінал:
    ```bash
    Ctrl + Alt + F2
    ```

2. Авторизуйся:
    ```bash
    login: ваш_логін
    password: ваш_пароль
    ```

3. Запусти діагностику:
    ```bash
    journalctl -b            # Логи останнього запуску
    systemctl --failed       # Зламані сервіси
    systemctl list-units --state=failed
    ```

---

## 💾 Випадок B: Система не стартує — Live USB

1. Завантажся з Live USB  
2. Відкрий термінал  
3. Переглянь розділи:
    ```bash
    lsblk
    ```
4. Змонтуй кореневий розділ:
    ```bash
    sudo mkdir /mnt/arch
    sudo mount /dev/sdXY /mnt/arch
    ```
    > Замініть `sdXY` на свій розділ (наприклад, `sda2`).

5. Додатково змонтуй інші розділи:
    ```bash
    sudo mount --bind /dev /mnt/arch/dev
    sudo mount --bind /proc /mnt/arch/proc
    sudo mount --bind /sys /mnt/arch/sys
    sudo mount /dev/sdXZ /mnt/arch/boot   # якщо є окремий /boot
    ```

6. Перейди в chroot:
    ```bash
    sudo chroot /mnt/arch
    ```

---

## 🚨 Типові помилки та рішення

!!! failure "Failed to mount /etc/fstab"
    **Причина:** Помилка у `fstab`  
    **Рішення:**
    ```bash
    nano /etc/fstab
    ```
    Закоментуй проблемні рядки → `Ctrl+O`, `Enter`, `Ctrl+X`.

!!! failure "Kernel panic - not syncing"
    **Причина:** Пошкоджене ядро або initramfs  
    **Рішення:**
    ```bash
    mkinitcpio -P
    pacman -S linux
    mkinitcpio -P
    ```

!!! failure "GRUB error 15"
    **Причина:** Пошкоджений GRUB  
    **Рішення:**
    ```bash
    grub-install /dev/sdX
    grub-mkconfig -o /boot/grub/grub.cfg
    ```

---

## 🛠️ Корисні команди

| Команда | Призначення |
|---------|-------------|
| `journalctl -b` | Перегляд логів останнього завантаження для пошуку причин збою |
| `systemctl --failed` | Показує сервіси, які не змогли запуститися |
| `mkinitcpio -P` | Пересоздає initramfs для всіх ядер (потрібно після оновлень чи виправлень) |
| `grub-install /dev/sdX` | Встановлює GRUB на вибраний диск (`/dev/sda`, `/dev/nvme0n1` тощо) |
| `grub-mkconfig -o /boot/grub/grub.cfg` | Генерує новий конфігураційний файл GRUB |
| `fsck /dev/sdXY` | Перевірка та відновлення файлової системи на розділі |
| `pacman -Syu` | Оновлення системи та всіх пакетів до останньої версії |
| `pacman -Sc` | Очищення кешу pacman, залишає тільки актуальні пакети |
| `nano /etc/fstab` | Редагування таблиці монтування дисків |

## Вихід і перезавантаження
```bash
exit
```
```bash
sudo umount -R /mnt/arch
```
```bash
reboot
```

## 📝 Поради

    - Завжди роби бекап fstab перед змінами
    - Не видаляй старі ядра одразу після оновлення
    - Перевіряй UUID після зміни розділів
    - Тримай Live USB під рукою
    - Регулярно очищай кеш pacman і логи
