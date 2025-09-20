---
tags:
  - Windows
  - Windows Defender
---

# Виправлення проблем з Windows Defender

## 1. Відновлення системних файлів
```bash
Dism /Online /Cleanup-Image /RestoreHealth
```

## 2. Сканування системи
```bash
sfc /scannow
```