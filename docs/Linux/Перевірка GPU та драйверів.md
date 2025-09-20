---
tags:
- Linux
- Додаток
---

# Перевірка GPU та драйверів

!!! note "Цей скрипт автоматично перевіряє стан OpenGL, OpenCL та Vulkan на вашому комп'ютері, а також показує інформацію про драйвери GPU. У разі відсутності потрібних утиліт, він їх встановлює."

```bash
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
    echo "Устанавливаю $pkg..."
    sudo apt update
    sudo apt install -y "$pkg"
  fi
}

# Устанавливаем нужные утилиты, если нет
auto_install glxinfo mesa-utils
auto_install clinfo clinfo
auto_install vulkaninfo vulkan-tools

echo "=== OpenGL Info ==="
glxinfo | grep "OpenGL"

echo -e "\n=== OpenCL Devices ==="
if clinfo | grep -q "Platform Name"; then
  clinfo | grep "Platform Name"
else
  echo "OpenCL устройства не найдены."
fi

echo -e "\n=== Vulkan Devices ==="
vulkaninfo 2>/dev/null | grep deviceName | sort | uniq

echo -e "\n=== GPU Driver Info ==="
lspci -k | grep -EA3 'VGA|3D'

echo -e "\n=== Итог ==="

if glxinfo | grep -q "OpenGL"; then
  echo "OpenGL: работает"
else
  echo "OpenGL: не работает"
fi

if clinfo | grep -q "Platform Name"; then
  echo "OpenCL: работает"
else
  echo "OpenCL: не работает"
fi

if vulkaninfo 2>/dev/null | grep -q "deviceName"; then
  echo "Vulkan: работает"
else
  echo "Vulkan: не работает"
fi

distro=$(detect_distro)
if ! clinfo | grep -q "Platform Name"; then
  echo
  echo "Рекомендации по установке OpenCL для $distro:"
  case $distro in
    manjaro)
      echo "sudo pacman -S opencl-mesa"
      ;;
    neon)
      echo "sudo apt install mesa-opencl-icd ocl-icd-libopencl1"
      ;;
    ubuntu)
      echo "sudo apt install mesa-opencl-icd ocl-icd-libopencl1"
      ;;
    linuxmint)
      echo "sudo apt install mesa-opencl-icd"
      ;;
    *)
      echo "Попробуйте установить OpenCL драйверы, подходящие вашему дистрибутиву."
      ;;
  esac
fi
```