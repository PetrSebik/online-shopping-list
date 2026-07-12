{% load static %}
const CACHE_NAME = "home-hub-v1";
const PRECACHE_URLS = [
    "{% static 'base.css' %}",
    "{% static 'icon/icon-192.png' %}",
    "{% static 'icon/icon-512.png' %}",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((names) =>
            Promise.all(
                names.filter((name) => name !== CACHE_NAME).map((name) => caches.delete(name))
            )
        )
    );
    self.clients.claim();
});

// Cache-first for static assets, network-only for everything else (pages/HTMX/API)
// so shopping list / recipe / house-construction data is never served stale.
self.addEventListener("fetch", (event) => {
    const url = new URL(event.request.url);
    if (event.request.method !== "GET" || url.pathname.indexOf("/static/") !== 0) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) {
                return cached;
            }
            return fetch(event.request).then((response) => {
                const clone = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                return response;
            });
        })
    );
});
