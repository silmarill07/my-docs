---
title: "Автоматизація Distrobox на атомарних системах"
date: 2026-07-01
draft: false
tags: ["linux", "distrobox"]
image: "1.png"
description: "Створення зручних команд для автоматизації встановлення, видалення та оновлення програм у Distrobox на Fedora Atomic, Kinoite, Silverblue та інших атомарних системах."
---

На атомарних дистрибутивах, таких як Fedora Kinoite, Silverblue або інших системах на базі `rpm-ostree`, більшість користувацьких програм зручно встановлювати через **Distrobox**. Проте постійно вводити довгі команди не дуже комфортно.

У цій статті буде створено набір функцій, які значно спрощують роботу з Distrobox:

* `dbi` — встановлення програм із репозиторію або локального RPM-файлу;
* `dbr` — повне видалення програми разом із непотрібними залежностями;
* `dbup` — оновлення всіх пакетів у контейнері;
* `dbcc` — очищення кешу та видалення непотрібних залежностей.

> [!TIP]
> Інструкція однаково підходить для Bash і Zsh. Потрібно лише відкрити відповідний файл конфігурації оболонки.

---

## Крок 1. Відкрийте файл конфігурації оболонки

Для **Zsh**:

```bash
nano ~/.zshrc
```

Для **Bash**:

```bash
nano ~/.bashrc
```

---

## Крок 2. Додайте функції автоматизації

Вставте наведений нижче скрипт наприкінці файлу конфігурації.

> [!NOTE]
> Скрипт автоматично перевіряє наявність Distrobox, за потреби створює контейнер, встановлює програми, експортує ярлики до головної системи та дозволяє швидко оновлювати або видаляти встановлені пакети.

```bash
# ==============================================================================
# --- Скрипти автоматизації Distrobox для smv ---
# ==============================================================================

# Вспомогательная функция проверки наличия Distrobox в системе
_check_distrobox() {
    if ! command -v distrobox &> /dev/null; then
        echo "❌ Ошибка: Distrobox не установлен в основной системе!"
        echo "💡 Для установки на Fedora Atomic (Kinoite/Silverblue) выполни:"
        echo "   rpm-ostree install distrobox && rpm-ostree rebase"
        echo "   (после чего перезагрузи компьютер)"
        return 1
    fi
    return 0
}

# 1. Функция Установки из репозитория или локального RPM (dbi)
dbox-install() {
    _check_distrobox || return 1

    if [ -z "$1" ]; then
        echo "❌ Ошибка: Укажи название пакета или путь к RPM."
        return 1
    fi

    local CONTAINER="smv"
    local INPUT="$1"
    local PKG=""

    if ! distrobox list | grep -q "$CONTAINER"; then
        echo "📦 Контейнер '$CONTAINER' не найден. Создаю новый..."

        distrobox create --name "$CONTAINER" --image registry.fedoraproject.org/fedora:latest --yes

        distrobox enter "$CONTAINER" -- sudo sh -c "echo 'LANG=ru_RU.UTF-8' >> /etc/environment"
        distrobox enter "$CONTAINER" -- sudo sh -c "echo 'LC_ALL=ru_RU.UTF-8' >> /etc/environment"
        distrobox enter "$CONTAINER" -- sh -c "echo 'export LANG=ru_RU.UTF-8' >> ~/.bashrc"
        distrobox enter "$CONTAINER" -- sh -c "echo 'export LC_ALL=ru_RU.UTF-8' >> ~/.bashrc"

        distrobox enter "$CONTAINER" -- sudo dnf5 install -y glibc-langpack-ru qt5-qttranslations qt6-qttranslations
    fi

    if [[ "$INPUT" == *.rpm ]]; then

        if [ ! -f "$INPUT" ]; then
            echo "❌ Файл не знайдено."
            return 1
        fi

        distrobox enter "$CONTAINER" -- sudo dnf5 install -y "$INPUT" || return 1

        PKG=$(rpm -qp --queryformat '%{NAME}\n' "$INPUT")

    else

        PKG="$INPUT"

        distrobox enter "$CONTAINER" -- sudo dnf5 install -y "$PKG" || return 1

    fi

    distrobox enter "$CONTAINER" -- distrobox-export --app "$PKG"

    echo "✅ Програму успішно встановлено."
}

# 2. Видалення програм
dbox-remove() {

    _check_distrobox || return 1

    local CONTAINER="smv"
    local PKG="$1"

    distrobox enter "$CONTAINER" -- distrobox-export --app "$PKG" --delete
    distrobox enter "$CONTAINER" -- sudo dnf5 remove -y "$PKG"
    distrobox enter "$CONTAINER" -- sudo dnf5 autoremove -y

    echo "🗑️ Програму видалено."
}

alias dbi='dbox-install'
alias dbr='dbox-remove'
alias dbup='_check_distrobox && distrobox enter smv -- sudo dnf5 upgrade -y'
alias dbcc='_check_distrobox && distrobox enter smv -- sudo dnf5 autoremove -y && distrobox enter smv -- sudo dnf5 clean all'
```

> [!IMPORTANT]
> Скрипт використовує контейнер із назвою `smv`. Якщо ваш контейнер має іншу назву, замініть значення змінної `CONTAINER` у всіх функціях.

---

## Додаткові пакети (необов'язково)

Для коректного відображення перекладів Qt-програм можна встановити пакети локалізації:

```bash
distrobox enter smv -- sudo dnf5 install -y qt5-qttranslations qt6-qttranslations
```

> [!TIP]
> Якщо ви вже використовуєте наведений вище скрипт без змін, цей крок можна пропустити — потрібні пакети встановлюються автоматично під час створення контейнера.

---

## Крок 3. Застосуйте зміни

Для **Zsh**:

```bash
source ~/.zshrc
```

Для **Bash**:

```bash
source ~/.bashrc
```

---

# Використання

Після застосування налаштувань можна користуватися новими командами.

Встановлення програми:

```bash
dbi vlc
```

Встановлення локального RPM:

```bash
dbi ~/Завантаження/program.rpm
```

Видалення програми:

```bash
dbr vlc
```

Оновлення всіх пакетів контейнера:

```bash
dbup
```

Очищення залежностей та кешу:

```bash
dbcc
```

> [!NOTE]
> Під час першого запуску `dbi` контейнер буде створено автоматично, якщо він ще не існує.

---

# Підсумок

Після налаштування цих функцій робота з Distrobox стає значно швидшою. Замість довгих команд достатньо використовувати короткі `dbi`, `dbr`, `dbup` і `dbcc`, що робить встановлення, оновлення та видалення програм майже таким самим зручним, як у звичайному дистрибутиві Linux.
