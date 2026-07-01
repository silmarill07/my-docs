---
title: "Service Worker — офлайн-режим для будь-якого сайту"
date: 2026-06-27
draft: false
tags: ["other", "service sorker"]
image: "1.png"
description: "Перетворіть свій сайт на вебзастосунок, який може працювати навіть без підключення до Інтернету."
---

## Що таке Service Worker?

**Service Worker** — це спеціальний скрипт браузера, який працює у фоновому режимі та може:

* кешувати файли сайту;
* завантажувати сторінки швидше;
* відкривати сайт без доступу до Інтернету;
* перехоплювати мережеві запити.

> [!IMPORTANT]
> **Service Worker працює лише через HTTPS або на `localhost` під час розробки.**
> Якщо сайт відкритий через звичайний HTTP, браузер не зареєструє Service Worker.

---

## Швидкий старт

### Крок 1. Створіть файл `service-worker.js`

Створіть файл у корені проєкту.

```javascript
const CACHE_NAME = 'my-site-v1';

const urlsToCache = [
  './',
  './index.html',
  './style.css',
  './script.js'
];

// Встановлення Service Worker
self.addEventListener('install', event => {
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Перехоплення запитів
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

// Оновлення кешу
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      )
    )
  );

  self.clients.claim();
});
```

> [!TIP]
> `self.skipWaiting()` та `self.clients.claim()` дозволяють новій версії Service Worker активуватися одразу після оновлення без необхідності повторного відкриття вкладки.

---

### Крок 2. Зареєструйте Service Worker

Перед закривальним тегом `</body>` додайте:

```html
<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./service-worker.js')
            .then(() => console.log('Service Worker registered'))
            .catch(error => console.error(error));
    });
}
</script>
```

---

### Готово

Після першого відкриття сайту всі файли буде закешовано, і він зможе працювати без доступу до Інтернету.

---

## Налаштування кешу

Змініть лише два параметри.

### Назва кешу

```javascript
const CACHE_NAME = 'your-site-name-v1';
```

При кожному оновленні сайту достатньо змінити номер версії.

Наприклад:

```javascript
const CACHE_NAME = 'your-site-name-v2';
```

---

### Файли для кешування

```javascript
const urlsToCache = [
    './',
    './index.html',
    './about.html',
    './contact.html',

    './css/style.css',
    './css/responsive.css',

    './js/main.js',
    './js/utils.js',

    './images/logo.png',
    './icons/menu.svg'
];
```

> [!NOTE]
> Обов'язково кешуйте:
>
> * HTML-сторінки;
> * CSS;
> * JavaScript;
> * логотип;
> * важливі іконки;
> * критичні зображення.

> [!WARNING]
> Не рекомендується кешувати:
>
> * великі відеофайли;
> * великі фотогалереї;
> * сторонні ресурси (`https://...`);
> * контент, що часто змінюється (новини, ціни, статистика).

---

## Офлайн-індикатор (необов'язково)

### HTML

```html
<div id="offline-indicator" class="offline-indicator" style="display:none">
    <span>Офлайн-режим</span>
</div>

<div class="container">
    <!-- Ваш контент -->
</div>
```

### CSS

```css
.offline-indicator {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background: #e74c3c;
    color: white;
    text-align: center;
    padding: 8px 0;
    font-size: .9rem;
    font-weight: 600;
    z-index: 1000;
}

.container.offline-mode {
    margin-top: 40px;
}
```

### JavaScript

```javascript
function updateOnlineStatus() {

    const offlineIndicator = document.getElementById('offline-indicator');
    const container = document.querySelector('.container');

    if (navigator.onLine) {
        offlineIndicator.style.display = 'none';
        container.classList.remove('offline-mode');
    } else {
        offlineIndicator.style.display = 'block';
        container.classList.add('offline-mode');
    }

}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
window.addEventListener('load', updateOnlineStatus);
```

---

## Додавання офлайн-сторінки

Для кращого користувацького досвіду рекомендується створити файл `offline.html` і додати його до списку кешування.

```javascript
const urlsToCache = [
    './',
    './offline.html',
    './style.css',
    './script.js'
];
```

> [!TIP]
> Якщо потрібний ресурс недоступний через відсутність Інтернету, можна показувати користувачу `offline.html` замість стандартної помилки браузера.

---

## Перевірка роботи

### Перевірка Service Worker

1. Відкрийте сайт.
2. Натисніть `F12`.
3. Перейдіть у **Application → Service Workers**.
4. Статус має бути **Activated and is running**.

---

### Перевірка кешу

Відкрийте:

`Application → Cache Storage`

Там повинен з'явитися створений кеш.

---

### Перевірка офлайн-режиму

1. Відкрийте сайт.
2. Дочекайтеся завершення кешування.
3. Вимкніть Інтернет.
4. Оновіть сторінку.

Сайт повинен відкритися навіть без мережі.

---

## Структура проєкту

```text
your-project/
├── index.html
├── style.css
├── script.js
├── service-worker.js
├── offline.html
├── images/
└── icons/
```

---

## Типові проблеми

### Помилка 404

> [!CAUTION]
> `Failed to register ServiceWorker: 404`

> [!TIP]
> Переконайтеся, що файл `service-worker.js` знаходиться в корені сайту та реєструється через:
>
> ```javascript
> navigator.serviceWorker.register('./service-worker.js')
> ```

---

### Service Worker не оновлюється

> [!CAUTION]
> Після зміни коду сайт продовжує працювати зі старою версією.

> [!TIP]
> Змініть:
>
> ```javascript
> const CACHE_NAME = 'my-site-v1';
> ```
>
> на
>
> ```javascript
> const CACHE_NAME = 'my-site-v2';
> ```
>
> або очистьте кеш браузера.

---

### Занадто великий кеш

> [!CAUTION]
> Сайт займає багато місця.

> [!TIP]
> Кешуйте лише критично важливі ресурси, а великі відео та галереї завантажуйте через мережу.

---

## Поширені запитання

### Чи працює на мобільних пристроях?

Так. Service Worker підтримується Chrome, Edge, Firefox, Safari та більшістю сучасних мобільних браузерів.

### Чи потрібен HTTPS?

Так. Виняток — `localhost` під час розробки.

### Як оновити кеш?

Змініть версію `CACHE_NAME`.

### Чи можна кешувати API?

Так, але для цього рекомендується використовувати окремі стратегії кешування, наприклад **Network First** або **Stale While Revalidate**.

---

## Висновок

Service Worker додає сайту підтримку офлайн-режиму та є однією з основних технологій **Progressive Web Apps (PWA)**.

Після налаштування сайт:

* швидше завантажується;
* може працювати без Інтернету;
* забезпечує кращий користувацький досвід;
* готовий до подальшого розвитку як PWA.

> [!TIP]
> Для невеликих сайтів достатньо наведеного прикладу. Якщо проєкт розростеться, варто звернути увагу на **Workbox**, який значно спрощує роботу з кешуванням і оновленнями Service Worker.
