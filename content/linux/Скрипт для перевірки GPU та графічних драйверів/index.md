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

auto_install() {
  local cmd=$1
  local pkg=$2
  if ! command -v "$cmd" &>/dev/null; then
    echo "Встановлюю $pkg..."
    sudo apt update
    sudo apt install -y "$pkg"
  fi
}

# Встановлюємо потрібні утиліти, якщо вони відсутні
auto_install glxinfo mesa-utils
auto_install clinfo clinfo
auto_install vulkaninfo vulkan-tools

echo "=== OpenGL Info ==="
glxinfo | grep "OpenGL"

echo -e "\n=== OpenCL Devices ==="
if clinfo | grep -q "Platform Name"; then
  clinfo | grep "Platform Name"
else
  echo "OpenCL пристроїв не знайдено."
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

distro=$(detect_distro)
if ! clinfo | grep -q "Platform Name"; then
  echo
  echo "Рекомендації щодо встановлення OpenCL для $distro:"
  case $distro in
    neon)
      echo "sudo apt install mesa-opencl-icd ocl-icd-libopencl1"
      ;;
    ubuntu)
      echo "sudo apt install mesa-opencl-icd ocl-icd-libopencl1"
      ;;
    linuxmint)
      echo "sudo apt install mesa-opencl-icd"
      ;;
    fedora)
      echo "sudo dnf install rocm-opencl mesa-libOpenCL"
      ;;
    *)
      echo "Спробуйте встановити OpenCL драйвери, які підходять для вашого дистрибутива."
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