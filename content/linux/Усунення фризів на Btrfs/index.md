---
title: "Усунення фризів на Btrfs"
date: 2026-06-27
draft: false
tags: ["linux", "btrfs"]
image: "1.png"
description: "Якщо під час роботи системи на файловій системі Btrfs спостерігаються короткочасні зависання або фризи, їх можна зменшити, змінивши параметри монтування..."
slug: "fix-btrfs-freezes"
---

Якщо під час роботи системи на файловій системі **Btrfs** спостерігаються короткочасні зависання або фризи, їх можна зменшити, змінивши параметри монтування, увімкнувши регулярне очищення TRIM та налаштувавши ліміти запису в оперативну пам'ять.

## Вимкнення планувальника введення-виведення

Виконайте команду:

```bash
echo none | sudo tee /sys/block/sda/queue/scheduler
```

> [!IMPORTANT]
> Якщо система встановлена не на диску `sda`, замініть його на свій пристрій, наприклад `nvme0n1` або `vda`.

---

## Налаштування параметрів монтування

Відкрийте файл `fstab`:

```bash
sudo nano /etc/fstab
```

Для кожного Btrfs-розділу додайте параметри:

```text
noatime,nodiscard,commit=5
```

> [!NOTE]
> У результаті записи можуть виглядати так:
>
> ```text
> UUID=16695623-ada8-4a90-9ccc-62626cfc56ca /              btrfs subvol=/@,defaults,noatime,nodiscard,commit=5,compress=zstd:1 0 0
> UUID=16695623-ada8-4a90-9ccc-62626cfc56ca /home          btrfs subvol=/@home,defaults,noatime,nodiscard,commit=5,compress=zstd:1 0 0
> UUID=16695623-ada8-4a90-9ccc-62626cfc56ca /var/cache     btrfs subvol=/@cache,defaults,noatime,nodiscard,commit=5,compress=zstd:1 0 0
> UUID=16695623-ada8-4a90-9ccc-62626cfc56ca /var/log       btrfs subvol=/@log,defaults,noatime,nodiscard,commit=5,compress=zstd:1 0 0
> ```

---

## Увімкнення автоматичного TRIM

Активуйте таймер `fstrim`:

```bash
sudo systemctl enable fstrim.timer
```

---

## Налаштування лімітів запису в оперативну пам'ять

Створіть файл конфігурації:

```bash
sudo nano /etc/sysctl.d/99-btrfs-fixes.conf
```

Додайте до нього:

```text
vm.dirty_background_bytes = 67108864
vm.dirty_bytes = 134217728
```

---

## Перезавантаження системи

Після внесення змін перезавантажте комп'ютер:

```bash
sudo reboot
```

---

## Перевірка

Після запуску системи виконайте:

```bash
mount | grep btrfs
```

> [!TIP]
> Якщо все налаштовано правильно, параметр `discard=async` більше не повинен відображатися у виводі команди.
