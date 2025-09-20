---
tags:
  - Linux
  - GitHub
---

# Завантаження файлів на GitHub

## Кроки

### 1. Перевірити SSH-ключ (зазвичай `id_ed25519`)
```bash
ls ~/.ssh
```

### 2. Перевірити з'єднання з GitHub
```bash
ssh -T git@github.com
```

!!! note "Очікуваний результат:"
    Hi silmarill07! You've successfully authenticated...

### 3. Перейти в папку з проектом
``
cd /шлях/до/папки/репозиторію
``

!!! note "Якщо потрібно перемкнути гілку використовивати команду ``git checkout`` (Наприклад: ``git checkout gh-pages``)"

### 4. Додати нові файли до git
```bash
git add .
```

### 5. Закомітити зміни
```bash
git commit -m "Опис змін"
```

### 6. Відправити на GitHub
```bash
git push origin gh-pages
```

```bash
git push origin main
```

!!! tip "Порада"
    Перевіряйте статус командою git status, щоб бачити додані та незбережені зміни перед комітом.