// Flick-to-navigate between the shopping list and the recipe book, with a
// live "two pages side by side" slide: as soon as a drag direction is
// recognized, the destination page's HTML is fetched and shown as a
// non-interactive preview panel sliding in from the opposite edge, in sync
// with the real page sliding out — so both are visible and moving together,
// tiling edge-to-edge, instead of a blank gap opening up behind the page
// being dragged away.
//
// The preview is a static snapshot (its own scripts/htmx aren't executed —
// it's discarded the moment the real navigation lands, so nothing about it
// needs to be interactive). If the fetch hasn't resolved by the time the
// user releases, it falls back to the plain "outgoing page fades to a
// partial offset" exit, no worse than before this preview existed.
//
// Navigation uses location.replace(), not location.href/assign(), so a swipe
// swaps the current history entry instead of pushing a new one. Otherwise
// hopping back and forth (list -> detail -> swipe to shopping -> swipe back
// to detail) stacks duplicate entries and the OS back button lands on an
// intermediate stop instead of where you actually came from.
(function () {
    const SWIPE_THRESHOLD_PX = 70;
    const MAX_VERTICAL_RATIO = 0.6;
    const DRAG_DEAD_ZONE_PX = 12;
    const FREE_DRAG_PX = 120;
    const RESISTANCE = 0.35;
    const FALLBACK_EXIT_PCT = 55;
    const FALLBACK_EXIT_MIN_OPACITY = 0.45;
    const COMMIT_MS = 140;
    const SNAPBACK_MS = 180;
    const ENTRY_DIRECTION_KEY = "swipeEntryDirection";
    const LAST_RECIPE_URL_KEY = "lastRecipeUrl";

    const path = window.location.pathname;
    const isShoppingPage = path.startsWith("/shopping/");
    const isRecipePage = path.startsWith("/recipe/");

    if (isRecipePage) {
        localStorage.setItem(LAST_RECIPE_URL_KEY, path + window.location.search);
    }

    if (!isShoppingPage && !isRecipePage) return;

    const stage = document.querySelector(".swipe-stage");
    const viewport = document.querySelector(".swipe-viewport");
    if (!stage || !viewport) return;

    // Only relevant on the fallback (no-preview) path — see loadPreview().
    const entryDirection = sessionStorage.getItem(ENTRY_DIRECTION_KEY);
    if (entryDirection) {
        sessionStorage.removeItem(ENTRY_DIRECTION_KEY);
        viewport.classList.add(entryDirection === "left" ? "swipe-enter-from-left" : "swipe-enter-from-right");
    }

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function targetFor(direction) {
        return direction === "left"
            ? (localStorage.getItem(LAST_RECIPE_URL_KEY) || "/recipe/list/")
            : "/shopping/list/";
    }

    function ensureStylesheet(href) {
        if (!href) return;
        const already = document.querySelector(`link[rel="stylesheet"][href="${href}"]`);
        if (already) return;
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = href;
        document.head.appendChild(link);
    }

    // Fetches the destination page, pulls in any stylesheet it needs that
    // this page doesn't already have loaded, and returns the markup for its
    // .swipe-viewport — everything needed to render an accurate preview.
    async function fetchPreviewHtml(url) {
        try {
            const response = await fetch(url, {credentials: "same-origin"});
            if (!response.ok) return null;
            const html = await response.text();
            const doc = new DOMParser().parseFromString(html, "text/html");
            doc.querySelectorAll('link[rel="stylesheet"]').forEach((link) => {
                ensureStylesheet(link.getAttribute("href"));
            });
            const source = doc.querySelector(".swipe-viewport");
            return source ? source.innerHTML : null;
        } catch (err) {
            return null;
        }
    }

    // 1:1 tracking for the first FREE_DRAG_PX, then progressively resisted,
    // so a long drag doesn't send the page all the way off mid-gesture.
    function dampen(distance) {
        if (distance <= FREE_DRAG_PX) return distance;
        return FREE_DRAG_PX + (distance - FREE_DRAG_PX) * RESISTANCE;
    }

    let startX = null;
    let startY = null;
    let dragDirection = null; // "left" | "right" | null
    let lastDampened = 0;
    let preview = null; // {el, ready} for the in-flight/loaded ghost panel

    function startPreview(direction) {
        const el = document.createElement("div");
        el.className = "swipe-preview";
        el.style.transition = "none";
        el.style.transform = `translateX(${direction === "left" ? window.innerWidth : -window.innerWidth}px)`;
        stage.appendChild(el);
        const state = {el, ready: false};
        fetchPreviewHtml(targetFor(direction)).then((html) => {
            if (state.discarded || html === null) return;
            el.innerHTML = html;
            state.ready = true;
            // Snap to wherever the drag already is — no animation, just catch up.
            positionPreview(state, direction, lastDampened);
        });
        return state;
    }

    function positionPreview(state, direction, dampened) {
        if (!state || !state.el) return;
        const base = direction === "left" ? window.innerWidth : -window.innerWidth;
        state.el.style.transform = `translateX(${base + dampened}px)`;
    }

    function discardPreview(state) {
        if (!state) return;
        state.discarded = true;
        if (state.el && state.el.parentNode) state.el.remove();
    }

    function clearInlineStyles(el) {
        el.style.transition = "";
        el.style.transform = "";
        el.style.opacity = "";
    }

    function snapBack(direction) {
        const duration = reducedMotion ? 0 : SNAPBACK_MS;
        const transition = reducedMotion ? "none" : `transform ${duration}ms ease-out, opacity ${duration}ms ease-out`;

        viewport.style.transition = transition;
        viewport.style.transform = "translateX(0)";
        viewport.style.opacity = "";

        const activePreview = preview;
        if (activePreview && activePreview.el) {
            activePreview.el.style.transition = transition;
            activePreview.el.style.transform = `translateX(${direction === "left" ? window.innerWidth : -window.innerWidth}px)`;
        }
        preview = null;

        const finish = () => {
            clearInlineStyles(viewport);
            discardPreview(activePreview);
        };
        if (duration === 0) {
            finish();
        } else {
            viewport.addEventListener("transitionend", finish, {once: true});
        }
    }

    viewport.addEventListener("touchstart", (event) => {
        if (event.touches.length !== 1) return;
        startX = event.touches[0].clientX;
        startY = event.touches[0].clientY;
        dragDirection = null;
        lastDampened = 0;
        viewport.style.transition = "none";
        if (preview) {
            discardPreview(preview);
            preview = null;
        }
    }, {passive: true});

    viewport.addEventListener("touchmove", (event) => {
        if (startX === null) return;
        const touch = event.touches[0];
        const deltaX = touch.clientX - startX;
        const deltaY = touch.clientY - startY;

        if (!dragDirection) {
            if (Math.abs(deltaX) < DRAG_DEAD_ZONE_PX || Math.abs(deltaY) > Math.abs(deltaX) * MAX_VERTICAL_RATIO) {
                return;
            }
            if (isShoppingPage && deltaX < 0) {
                dragDirection = "left";
            } else if (isRecipePage && deltaX > 0) {
                dragDirection = "right";
            } else {
                return; // wrong direction for this page — leave scrolling alone
            }
            preview = startPreview(dragDirection);
        }

        // Committed to a horizontal drag now — stop the page from also scrolling.
        event.preventDefault();
        const dampened = dampen(Math.abs(deltaX)) * (dragDirection === "left" ? -1 : 1);
        lastDampened = dampened;
        viewport.style.transform = `translateX(${dampened}px)`;
        if (preview && preview.ready) {
            positionPreview(preview, dragDirection, dampened);
        } else {
            // No preview yet (still loading) — dim slightly so the drag still
            // has some feedback instead of looking inert.
            viewport.style.opacity = String(1 - Math.min(Math.abs(dampened) / window.innerWidth, 0.5));
        }
    }, {passive: false});

    viewport.addEventListener("touchend", (event) => {
        if (startX === null) return;
        const touch = event.changedTouches[0];
        const deltaX = touch.clientX - startX;
        const direction = dragDirection;
        const activePreview = preview;
        startX = null;
        dragDirection = null;
        preview = null;

        if (!direction) return;

        const passed = Math.abs(deltaX) >= SWIPE_THRESHOLD_PX;

        if (!passed) {
            preview = activePreview;
            snapBack(direction);
            return;
        }

        const target = targetFor(direction);
        const usingPreview = Boolean(activePreview && activePreview.ready);

        // Only the fallback path needs the destination to replay its own
        // entrance animation — with a working preview, the ghost already
        // finishes the motion, so the fresh page should just appear as-is.
        if (!usingPreview) {
            sessionStorage.setItem(ENTRY_DIRECTION_KEY, direction === "left" ? "right" : "left");
        }

        if (reducedMotion) {
            window.location.replace(target);
            return;
        }

        if (usingPreview) {
            const offscreenPx = direction === "left" ? -window.innerWidth : window.innerWidth;
            viewport.style.transition = `transform ${COMMIT_MS}ms ease-in`;
            viewport.style.transform = `translateX(${offscreenPx}px)`;
            activePreview.el.style.transition = `transform ${COMMIT_MS}ms ease-in`;
            activePreview.el.style.transform = "translateX(0)";
        } else {
            viewport.style.transition = `transform ${COMMIT_MS}ms ease-in, opacity ${COMMIT_MS}ms ease-in`;
            viewport.style.transform = `translateX(${direction === "left" ? -FALLBACK_EXIT_PCT : FALLBACK_EXIT_PCT}%)`;
            viewport.style.opacity = String(FALLBACK_EXIT_MIN_OPACITY);
            discardPreview(activePreview);
        }

        setTimeout(() => {
            window.location.replace(target);
        }, COMMIT_MS);
    }, {passive: true});

    viewport.addEventListener("touchcancel", () => {
        if (startX === null) return;
        startX = null;
        const wasDragging = dragDirection;
        dragDirection = null;
        if (wasDragging) snapBack(wasDragging);
    }, {passive: true});
})();
