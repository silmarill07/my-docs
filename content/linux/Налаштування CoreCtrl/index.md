---
title: "Налаштування CoreCtrl"
date: 2026-07-01
draft: false
tags: ["linux", "corectrl"]
image: "1.png"
description: "Покрокова інструкція зі встановлення, та автозапуску CoreCtrl без запиту пароля."
---
> [!INFO]
> **CoreCtrl** — це утиліта для керування параметрами процесора та відеокарти в Linux. Вона дозволяє створювати профілі продуктивності, змінювати параметри GPU, контролювати енергоспоживання та автоматично застосовувати налаштування для окремих програм.

У цій статті розглянуто встановлення CoreCtrl, налаштування автозапуску та запуск без постійного введення пароля.

---

## Крок 1. Встановіть CoreCtrl

### Arch Linux / CachyOS

```bash id="d4c1ny"
sudo pacman -S corectrl
```

### Debian / Ubuntu

```bash id="jn6xqi"
sudo apt install corectrl
```

### Fedora

```bash id="w8r9eh"
sudo dnf install corectrl
```

> [!TIP]
> Для інших дистрибутивів скористайтеся офіційною інструкцією проєкту CoreCtrl.

---

## Крок 2. Додайте CoreCtrl до автозапуску

Створіть каталог автозапуску, якщо він ще не існує:

```bash id="95mmtg"
mkdir -p ~/.config/autostart
```

Скопіюйте файл запуску:

```bash id="fzzb4l"
cp /usr/share/applications/org.corectrl.CoreCtrl.desktop ~/.config/autostart/
```

> [!NOTE]
> Наведена команда підходить для CachyOS. Для інших дистрибутивів шлях до `.desktop`-файлу може відрізнятися.

---

## Крок 3. Запуск без запиту пароля

Створіть правило Polkit:

```bash id="91lwdg"
sudo nano /etc/polkit-1/rules.d/90-corectrl.rules
```

Вставте в файл:

```javascript id="w8k42v"
polkit.addRule(function(action, subject) {
    if ((action.id == "org.corectrl.helper.init" ||
         action.id == "org.corectrl.helperkiller.init") &&
        subject.local == true &&
        subject.active == true &&
        subject.isInGroup("smv")) {
            return polkit.Result.YES;
    }
});
```

> [!IMPORTANT]
> Замініть `smv` на назву групи, до якої входить ваш користувач. У більшості дистрибутивів це `wheel` або `sudo`.

> [!TIP]
> Перевірити, до яких груп належить поточний користувач, можна командою:

```bash id="2gkk6e"
groups
```

---

## Перевірка

Перезапустіть CoreCtrl. Якщо правило Polkit налаштовано правильно, програма запускатиметься без запиту пароля.

> [!TIP]
> Усі актуальні команди та особливості налаштування для різних дистрибутивів можна знайти в офіційній документації CoreCtrl.

## Підсумок

Після виконання цих кроків CoreCtrl буде автоматично запускатися разом із системою та працюватиме без запиту пароля, що зробить керування продуктивністю значно зручнішим.
