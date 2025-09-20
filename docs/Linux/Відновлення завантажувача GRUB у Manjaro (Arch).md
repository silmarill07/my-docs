---
tags:
- Linux
- Manjaro (Arch)
---

# Відновлення завантажувача GRUB у Manjaro (Arch)

!!! tip "Підказка"
Використовуйте Live CD Manjaro для виконання нижченаведених кроків.

## Кроки відновлення

### 1. Відобразити всі диски:
```bash
sudo fdisk -l
```

### 2. Змонтувати кореневий розділ:
```bash
sudo mount -o subvol=@ /dev/sda2 /mnt
```

### 3. Змонтувати EFI-розділ:
```bash
sudo mount /dev/sda1 /mnt/boot/efi
```

### 4. Перейти у chroot:
```bash
sudo manjaro-chroot /mnt
```

### 5. Встановити GRUB:
```bash
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=Manjaro
update-grub
```

### 6. Вийти з chroot:
```bash
exit
```

### 7. Перезавантажити систему:
```bash
reboot
```