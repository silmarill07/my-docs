{{- $buildHash := now.Format "20060102150405" -}}
{{- $linuxImg := resources.Get "img/linux.png" | fingerprint -}}
{{- $windowsImg := resources.Get "img/windows.png" | fingerprint -}}
{{- $otherImg := resources.Get "img/other.png" | fingerprint -}}
const CACHE_VERSION = 'mydocs-{{ $buildHash }}';
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const PAGES_CACHE = `${CACHE_VERSION}-pages`;
const IMAGES_CACHE = `${CACHE_VERSION}-images`;

const SHELL_URLS = [
  '/',
  '/offline/index.html',
  '/covers.json',
  '{{ $linuxImg.RelPermalink }}',
  '{{ $windowsImg.RelPermalink }}',
  '{{ $otherImg.RelPermalink }}',
];

const SECTION_FALLBACKS = {
  'linux':   '{{ $linuxImg.RelPermalink }}',
  'windows': '{{ $windowsImg.RelPermalink }}',
  'other':   '{{ $otherImg.RelPermalink }}',
};

// ─── Install ────────────────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL_URLS))
      .then(() => self.skipWaiting())
  );
});

// ─── Activate ───────────────────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => !key.startsWith(CACHE_VERSION))
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
      .then(() => backgroundPrecache())
  );
});

// ─── Background precache ─────────────────────────────────────────────────────
async function backgroundPrecache() {
  let coverUrls = [];
  try {
    const res = await fetch('/covers.json');
    if (res.ok) coverUrls = await res.json();
  } catch (_) {}

  let pageUrls = [];
  try {
    const res = await fetch('/index.json');
    if (res.ok) {
      const index = await res.json();
      pageUrls = index.map(p => p.permalink).filter(Boolean);
    }
  } catch (_) {}

  const pagesCache = await caches.open(PAGES_CACHE);
  const imagesCache = await caches.open(IMAGES_CACHE);

  // Precache pages — only what's not yet cached
  for (const url of pageUrls) {
    const cached = await pagesCache.match(url);
    if (!cached) {
      try {
        const res = await fetch(url);
        if (res.ok) await pagesCache.put(url, res);
        await sleep(100);
      } catch (_) {}
    }
  }

  // Precache inline images found in cached pages
  const pageKeys = await pagesCache.keys();
  for (const req of pageKeys) {
    try {
      const res = await pagesCache.match(req);
      if (!res) continue;
      const html = await res.text();
      const imgUrls = extractImageUrls(html, req.url);

      for (const imgUrl of imgUrls) {
        const urlPath = new URL(imgUrl).pathname;
        if (coverUrls.includes(urlPath)) continue; // skip cover images
        const cached = await imagesCache.match(imgUrl);
        if (!cached) {
          try {
            const imgRes = await fetch(imgUrl);
            if (imgRes.ok) await imagesCache.put(imgUrl, imgRes);
            await sleep(150);
          } catch (_) {}
        }
      }
    } catch (_) {}
  }
}

function extractImageUrls(html, baseUrl) {
  const urls = [];
  const regex = /<img[^>]+src="([^"]+)"/gi;
  let match;
  while ((match = regex.exec(html)) !== null) {
    try {
      const abs = new URL(match[1], baseUrl).href;
      if (abs.startsWith(self.location.origin)) urls.push(abs);
    } catch (_) {}
  }
  return urls;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ─── Resume background precache when back online ─────────────────────────────
self.addEventListener('message', event => {
  if (event.data === 'online') {
    backgroundPrecache();
  }
});
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  if (url.origin !== self.location.origin) return;

  if (request.destination === 'document') {
    event.respondWith(networkFirstPage(request));
    return;
  }

  if (request.destination === 'image') {
    event.respondWith(handleImage(request, url));
    return;
  }

  if (['style', 'script', 'font'].includes(request.destination)) {
    event.respondWith(cacheFirst(request, SHELL_CACHE));
    return;
  }
});

async function networkFirstPage(request) {
  try {
    const res = await fetch(request);
    if (res.ok) {
      const cache = await caches.open(PAGES_CACHE);
      cache.put(request, res.clone());
    }
    return res;
  } catch (_) {
    const cached = await caches.match(request, { cacheName: PAGES_CACHE });
    if (cached) return cached;
    return caches.match('/offline/index.html');
  }
}

async function handleImage(request, url) {
  const coverUrls = await getCoverUrls();
  const isCover = coverUrls.includes(url.pathname);

  if (isCover) {
    // Cover: network first, fallback to section default image
    try {
      const res = await fetch(request);
      if (res.ok) return res;
    } catch (_) {}
    return sectionFallback(url.pathname);
  }

  // Inline image: cache first
  const cached = await caches.match(request, { cacheName: IMAGES_CACHE });
  if (cached) return cached;

  try {
    const res = await fetch(request);
    if (res.ok) {
      const cache = await caches.open(IMAGES_CACHE);
      cache.put(request, res.clone());
    }
    return res;
  } catch (_) {
    return sectionFallback(url.pathname);
  }
}

async function sectionFallback(pathname) {
  const section = pathname.split('/')[1];
  const fallbackPath = SECTION_FALLBACKS[section];
  if (fallbackPath) {
    const fallback = await caches.match(fallbackPath);
    if (fallback) return fallback;
    try { return await fetch(fallbackPath); } catch (_) {}
  }
  return new Response('', { status: 404 });
}

let _coverUrls = null;
async function getCoverUrls() {
  if (_coverUrls) return _coverUrls;
  try {
    const cached = await caches.match('/covers.json', { cacheName: SHELL_CACHE });
    const res = cached || await fetch('/covers.json');
    if (res && res.ok) {
      _coverUrls = await res.json();
      return _coverUrls;
    }
  } catch (_) {}
  return [];
}

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request, { cacheName });
  if (cached) return cached;
  try {
    const res = await fetch(request);
    if (res.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, res.clone());
    }
    return res;
  } catch (_) {
    return new Response('', { status: 503 });
  }
}
