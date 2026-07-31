---
title: "Установка Fedora 44 з Btrfs, Snapper та DNF5"
date: 2026-07-31
draft: false
tags: ["linux", "btrfs", "fedora", "snapper"]
image: "1.png"
description: "Встановлення Fedora 44 з файловою системою Btrfs, автоматичними знімками Snapper, grub-btrfs та інтеграцією з DNF5."
slug: "fedora-44-btrfs-snapper-dnf5"
---

# Установка Fedora 44 з Btrfs, Snapper та DNF5

> [!TIP]
> Дана конфігурація забезпечує автоматичне створення знімків системи під час встановлення або оновлення пакетів через термінал (`dnf5`) та графічні менеджери програм (GNOME Software або KDE Discover).

## Розмітка диска (Custom Storage)

Під час встановлення Fedora виберіть **Custom Storage** та створіть нову таблицю розділів **GPT**.

### Створення розділів

| Розділ | Тип | Точка монтування | Розмір |
|--------|-----|------------------|--------|
| EFI | EFI System Partition | `/boot/efi` | 1 GiB |
| Btrfs | Btrfs | Не вказується | Решта диска |

### Створення підтомів (Subvolumes)

Всередині розділу **Btrfs** створіть наступні підтоми.

| Підтом | Точка монтування |
|--------|------------------|
| `root` | `/` |
| `home` | `/home` |
| `opt` | `/opt` |
| `cache` | `/var/cache` |
| `log` | `/var/log` |
| `spool` | `/var/spool` |
| `temp` | `/var/temp` |
| `containers` | `/var/lib/containers` |
| `flatpak` | `/var/lib/flatpak` |
| `gdm` | `/var/lib/gdm` |
| `libvirt` | `/var/lib/libvirt` |

> [!IMPORTANT]
> Для Btrfs-розділу **не потрібно** задавати точку монтування. Вона призначається окремо для кожного підтому.

## Увімкнення стиснення ZSTD

Після завершення встановлення та першого завантаження системи увімкніть прозоре стиснення Btrfs.

```bash
sudo sed -i.bkp '/ btrfs / s/subvol=[^ ,]*/&,compress=zstd:1/' /etc/fstab
```

Після цього перезавантажте комп'ютер.

## Автоматичні знімки Snapper

Для налаштування **Snapper**, **grub-btrfs** та інтеграції з **DNF5** використайте офіційний репозиторій **SysGuides**.

Клонуйте репозиторій:

```bash
git clone https://github.com/SysGuides/sysguides-snapper-fedora
```

Перейдіть до каталогу та запустіть інсталятор:

```bash
cd sysguides-snapper-fedora
chmod +x install.sh
./install.sh
```

## Перевірка роботи

### Через термінал (CLI)

Встановіть будь-який пакет:

```bash
sudo dnf install htop
```

Переконайтеся, що створилися знімки:

```bash
sudo snapper list
```

### Через графічний інтерфейс (GUI)

Встановіть будь-який RPM-пакет через **GNOME Software** або **KDE Discover**.

Fedora 44 використовує бекенд **libdnf5**, тому Snapper автоматично створить знімки системи.

## Відкат змін

Щоб повернути систему до стану до встановлення або оновлення пакета, виконайте:

```bash
sudo snapper undochange <номер_pre>..<номер_post>
```

Наприклад:

```bash
sudo snapper undochange 25..26
```

> [!NOTE]
> Команда `undochange` не повертає систему до повного знімка, а лише скасовує зміни між двома знімками, що робить її безпечним способом відкату встановлення або оновлення пакетів.

> Після завершення інсталяції знімки Snapper автоматично з'являться в меню **GRUB**, що дозволить завантажитися в стан системи, збережений у будь-якому доступному знімку.
