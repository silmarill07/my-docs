---
title: "Скрипт для перевірки GPU та графічних драйверів"
date: 2026-07-07
draft: false
tags: ["linux", "applications"]
image: "1.png"
description: "Скрипт для автоматичної перевірки OpenGL, OpenCL, Vulkan і драйверів відеокарти в Linux з автоматичним встановленням необхідних утиліт."
slug: "gpu-driver-check-linux"
---
## Що перевіряє скрипт

Після запуску буде відображено:

* інформацію про **OpenGL**;
* список платформ **OpenCL**;
* знайдені пристрої **Vulkan**;
* інформацію про драйвери відеокарти;
* підсумок щодо працездатності OpenGL, OpenCL та Vulkan;
* рекомендації зі встановлення OpenCL, якщо він не знайдений.

## Створіть файл зі скриптом

Наприклад:

```bash id="drw0n9"
nano gpu-check.sh
```

Вставте наступний код:

```bash id="u4i0cf"
#!/bin/bash

detect_distro() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "$ID"
  else
    echo "unknown"
  fi
}

DISTRO=$(detect_distro)

auto_install() {
  local cmd=$1
  local apt_pkg=$2
  local dnf_pkg=$3

  if command -v "$cmd" &>/dev/null; then
    return
  fi

  echo "Встановлюю $cmd..."

  case "$DISTRO" in
    fedora)
      sudo dnf install -y $dnf_pkg
      ;;
    ubuntu|neon|linuxmint)
      sudo apt update
      sudo apt install -y $apt_pkg
      ;;
    *)
      echo "⚠️ Автоматичне встановлення не підтримується для $DISTRO."
      ;;
  esac
}

# Встановлення необхідних утиліт
auto_install glxinfo mesa-utils mesa-demos
auto_install clinfo clinfo clinfo
auto_install vulkaninfo vulkan-tools vulkan-tools

echo "=== OpenGL Info ==="
glxinfo | grep "OpenGL"

echo -e "\n=== OpenCL Devices ==="
if clinfo | grep -q "Platform Name"; then
  clinfo | grep "Platform Name"
else
  echo "OpenCL пристрої не знайдено."
fi

echo -e "\n=== Vulkan Devices ==="
vulkaninfo 2>/dev/null | grep deviceName | sort | uniq

echo -e "\n=== GPU Driver Info ==="
lspci -k | grep -EA3 'VGA|3D'

echo -e "\n=== Підсумок ==="

if glxinfo | grep -q "OpenGL"; then
  echo "OpenGL: працює"
else
  echo "OpenGL: не працює"
fi

if clinfo | grep -q "Platform Name"; then
  echo "OpenCL: працює"
else
  echo "OpenCL: не працює"
fi

if vulkaninfo 2>/dev/null | grep -q "deviceName"; then
  echo "Vulkan: працює"
else
  echo "Vulkan: не працює"
fi

if ! clinfo | grep -q "Platform Name"; then
  echo
  echo "Рекомендації щодо встановлення OpenCL для $DISTRO:"

  case "$DISTRO" in
    fedora)
      echo "sudo dnf install rocm-opencl"
      echo "sudo dnf install mesa-libOpenCL"
      ;;
    ubuntu|neon)
      echo "sudo apt install mesa-opencl-icd ocl-icd-libopencl1"
      ;;
    linuxmint)
      echo "sudo apt install mesa-opencl-icd"
      ;;
    *)
      echo "Встановіть OpenCL-драйвери, що відповідають вашому дистрибутиву та відеокарті."
      ;;
  esac
fi
```

---

## Зробіть файл виконуваним

```bash id="cvkqz7"
chmod +x gpu-check.sh
```

---

## Запустіть перевірку

```bash id="s4w0vf"
./gpu-check.sh
```

> [!TIP]
> Якщо необхідні утиліти відсутні, скрипт автоматично встановить їх. Для цього знадобляться права адміністратора.