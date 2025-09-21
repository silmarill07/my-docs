---
tags:
  - Other
  - Service Worker
---

# Service Worker - Офлайн режим для будь-якого сайту

> Перетворіть будь-який сайт на додаток, який працює без інтернету!

---

## Що таке Service Worker?

**Service Worker** — це "робот-помічник" в браузері, який:
- **Кешує** файли сайту на пристрої
- **Працює** навіть коли сайт закритий
- **Показує** сайт коли немає інтернету
- **Прискорює** завантаження сторінок

---

## Швидкий старт

### Крок 1: Створіть файл `service-worker.js`

Помістіть в **кореневу папку** проекту:

```javascript
// service-worker.js
const CACHE_NAME = 'my-site-v1';
const urlsToCache = [
  './',
  './index.html',
  './style.css',
  './script.js'
];

// Встановлюємо Service Worker і кешуємо файли
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Перехоплюємо запити і віддаємо з кешу
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Оновлюємо кеш при зміні Service Worker
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

### Крок 2: Додайте реєстрацію в HTML

Вставте перед закриваючим тегом `</body>`:

```html
<script>
    // Реєструємо Service Worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('./service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            }, function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
        });
    }
</script>
```

### Готово!

Ваш сайт тепер працює офлайн!

---

## Детальна настройка

### 1. Настройка кешу

Змініть тільки ці рядки в `service-worker.js`:

```javascript
// Назва кешу (будь-яке унікальне ім'я)
const CACHE_NAME = 'your-site-name-v1';

// Файли для кешування
const urlsToCache = [
  './',                    // головна сторінка
  './index.html',          // HTML сторінки
  './about.html',
  './contact.html',
  './css/style.css',       // CSS файли
  './css/responsive.css',
  './js/main.js',          // JavaScript файли
  './js/utils.js',
  './images/logo.png',     // важливі зображення
  './icons/menu.svg'       // іконки
];
```

### 2. Що кешувати?

#### !!! note "Обов'язково кешуйте:"
- HTML файли (`index.html`, `about.html`)
- CSS файли (`style.css`, `main.css`)
- JavaScript файли (`script.js`, `app.js`)
- Логотип і критичні зображення
- Важливі іконки

#### !!! warning "НЕ кешуйте:"
- Великі відео файли (>10MB)
- Багато фотографій з галереї
- Зовнішні ресурси (`https://...`)
- Часто змінюваний контент (новини, ціни)

### 3. Офлайн індикатор (опціонально)

#### HTML:
```html
<div id="offline-indicator" class="offline-indicator" style="display: none;">
    <span>Режим офлайн</span>
</div>

<div class="container">
    <!-- ваш контент -->
</div>
```

#### CSS:
```css
.offline-indicator {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #e74c3c;
    color: white;
    text-align: center;
    padding: 8px 0;
    font-size: 0.9rem;
    font-weight: 600;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.container.offline-mode {
    margin-top: 40px;
}
```

#### JavaScript (додати в HTML):
```html
<script>
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
</script>
```

---

## Перевірка роботи

### 1. **Через DevTools (Chrome/Edge)**

1. Відкрийте сайт
2. `F12` → **Application** → **Service Workers**
3. Повинен бути статус **"Activated and is running"**

### 2. **Перевірка кешу**

1. `F12` → **Application** → **Cache Storage**
2. Повинен з'явитися ваш кеш з файлами

### 3. **Тест офлайн режиму**

1. **Відкрийте сайт** (дайте час закешуватися)
2. **Відключіть Wi-Fi** на пристрої
3. **Оновіть сторінку** - повинна працювати!
4. З'явиться індикатор "Режим офлайн"

### 4. **Через браузер**

1. `F12` → **Network** → поставте галочку **"Offline"**
2. Оновіть сторінку - повинна працювати

---

## Структура проекту

```
your-project/
├── index.html          ← додати реєстрацію SW
├── style.css           ← додати стилі індикатора
├── script.js           ← ваш основний код
├── service-worker.js   ← новий файл
├── images/
│   └── logo.png        ← додати в кеш
└── icons/
    └── menu.svg        ← додати в кеш
```

---

## Часті проблеми

### **404 помилка Service Worker**

!!! danger "Проблема"
    `Failed to register ServiceWorker: 404`

!!! success "Рішення"
    - Переконайтеся що `service-worker.js` в кореневій папці
    - Використовуйте відносний шлях: `./service-worker.js`

### **Service Worker не оновлюється**

!!! danger "Проблема"
    Зміни не видні

!!! success "Рішення"
    - Змініть версію кешу: `my-site-v1` → `my-site-v2`
    - Очистіть кеш браузера: `Ctrl + Shift + Delete`

### **Великий розмір кешу**

!!! danger "Проблема"
    Додаток повільно завантажується

!!! success "Рішення"
    - Приберіть великі файли з `urlsToCache`
    - Кешуйте тільки критичні ресурси

---

## Приклади для різних сайтів

### **Лендинг сторінка**
```javascript
const CACHE_NAME = 'landing-v1';
const urlsToCache = [
  './',
  './index.html',
  './style.css',
  './script.js',
  './images/hero.jpg',
  './images/logo.svg'
];
```

### **Корпоративний сайт**
```javascript
const CACHE_NAME = 'company-site-v1';
const urlsToCache = [
  './',
  './index.html',
  './about.html',
  './services.html',
  './contact.html',
  './css/main.css',
  './js/app.js',
  './images/logo.png'
];
```

### **Портфоліо**
```javascript
const CACHE_NAME = 'portfolio-v1';
const urlsToCache = [
  './',
  './index.html',
  './portfolio.html',
  './styles/main.css',
  './js/portfolio.js',
  './images/avatar.jpg',
  './images/projects/preview1.jpg'
];
```

---

## FAQ

### **Q: Працює на мобільних?**
**A:** Так! Service Worker підтримується всіма сучасними браузерами.

### **Q: Потрібен HTTPS?**
**A:** Так, крім localhost. На продакшені потрібен HTTPS.

### **Q: Як оновити кеш?**
**A:** Змініть `CACHE_NAME` на нову версію (`v1` → `v2`).

### **Q: Скільки місця займає кеш?**
**A:** Залежить від розміру файлів. Зазвичай кілька МБ.

### **Q: Можна кешувати API дані?**
**A:** Так, але це складніше. Для початку кешуйте тільки статичні файли.

---

## Висновок

Service Worker перетворює будь-який сайт на **PWA (Progressive Web App)**, який:

- **Швидко завантажується**
- **Працює офлайн**
- **Відчувається як додаток**
- **Покращує користувацький досвід**

!!! tip "Головне"
    Копіюйте код, міняйте шляхи до файлів - і ваш сайт готовий до роботи без інтернету!