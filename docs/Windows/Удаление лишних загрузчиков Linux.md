---
tags:
  - Windows
---

# Видалення зайвих завантажувачів Linux

## 1. Відкрити cmd від імені адміністратора:
```bash
diskpart
```
```bash
list disk
```
```bash
sel disk
```
> Вкажіть номер диска з Windows, наприклад sel disk 2.
```bash
list vol
```
```bash
sel vol
```
> Вкажіть номер розділу зі "Системним".
```bash
assign letter=U:
```
```bash
exit
```

## 2. Перейдіть на диск з призначеною літерою:
```bash
U:
```
```bash
dir
```
```bash
cd EFI
```
```bash
dir
```

 - Видаліть непотрібний завантажувач, наприклад:
```bash
 rmdir /S ubuntu
 ```