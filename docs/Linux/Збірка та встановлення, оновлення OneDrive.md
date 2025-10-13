---
tags:
  - linux
  - onedrive
  - manjaro
  - debian
---
# Збірка та встановлення, оновлення OneDrive

## 1. Оновлення системи
- Debian/Ubuntu:
```bash
sudo apt update
```
- Manjaro:
``` bash
sudo pacman -Syu
```
## 2. Встановлення залежностей
- Debian/Ubuntu:
``` bash
sudo apt install build-essential libcurl4-openssl-dev libsqlite3-dev libnotify-dev libxml2-dev git pkg-config check libdbus-1-dev ldc
```
- Manjaro:
``` bash
sudo pacman -S --needed base-devel git curl sqlite libnotify libxml2 pkgconf
```
## 3. Збірка та встановлення OneDrive
- Перейти в папку з файлами OneDrive.
- Виконати:
``` bash
./configure
```
``` bash
make
```
``` bash
sudo make install
```
## 4. Видалення / Оновлення
!!! note "Видалити стару версію через вихідні файли:"

``` bash
sudo make uninstall
```
!!! note "Або вручну, якщо вихідних немає:"

``` bash
sudo rm /usr/local/bin/onedrive
```
``` bash
sudo rm -r /usr/local/share/doc/onedrive
```
``` bash
sudo rm -r /usr/local/share/man/man1/onedrive.1
```
``` bash
which onedrive
```