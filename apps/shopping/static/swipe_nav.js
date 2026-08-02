// Flick-to-navigate between the shopping list and the recipe book.
// Swipe left on the shopping list -> last-viewed recipe page (remembered in
// localStorage). Swipe right on any recipe page -> shopping list.
//
// The outgoing page is dragged live (transform follows the finger, with
// rubber-band resistance past a comfortable distance); releasing past the
// threshold finishes the slide-off and navigates, releasing short of it
// snaps back. The destination is prefetched (<link rel=prefetch>) the
// moment the drag direction is recognized, so by the time you release the
// real MPA navigation is warm instead of showing a network gap.
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

    const content = document.querySelector(".content");
    if (!content) return;

    const entryDirection = sessionStorage.getItem(ENTRY_DIRECTION_KEY);
    if (entryDirection) {
        sessionStorage.removeItem(ENTRY_DIRECTION_KEY);
        content.classList.add(entryDirection === "left" ? "swipe-enter-from-left" : "swipe-enter-from-right");
    }

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const prefetched = new Set();

    function prefetch(url) {
        if (prefetched.has(url)) return;
        prefetched.add(url);
        const link = document.createElement("link");
        link.rel = "prefetch";
        link.href = url;
        document.head.appendChild(link);
    }

    function targetFor(direction) {
        return direction === "left"
            ? (localStorage.getItem(LAST_RECIPE_URL_KEY) || "/recipe/list/")
            : "/shopping/list/";
    }

    // 1:1 tracking for the first FREE_DRAG_PX, then progressively resisted,
    // so a long drag doesn't send the page all the way off mid-gesture.
    function dampen(distance) {
        if (distance <= FREE_DRAG_PX) return distance;
        return FREE_DRAG_PX + (distance - FREE_DRAG_PX) * RESISTANCE;
    }

    function snapBack() {
        const duration = reducedMotion ? 0 : SNAPBACK_MS;
        content.style.transition = reducedMotion ? "none" : `transform ${duration}ms ease-out, opacity ${duration}ms ease-out`;
        content.style.transform = "translateX(0)";
        content.style.opacity = "";
        const clear = () => {
            content.style.transition = "";
            content.style.transform = "";
        };
        if (duration === 0) {
            clear();
        } else {
            content.addEventListener("transitionend", clear, {once: true});
        }
    }

    let startX = null;
    let startY = null;
    let dragDirection = null; // "left" | "right" | null

    content.addEventListener("touchstart", (event) => {
        if (event.touches.length !== 1) return;
        startX = event.touches[0].clientX;
        startY = event.touches[0].clientY;
        dragDirection = null;
        content.style.transition = "none";
    }, {passive: true});

    content.addEventListener("touchmove", (event) => {
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
            prefetch(targetFor(dragDirection));
        }

        // Committed to a horizontal drag now — stop the page from also scrolling.
        event.preventDefault();
        const dampened = dampen(Math.abs(deltaX)) * (dragDirection === "left" ? -1 : 1);
        content.style.transform = `translateX(${dampened}px)`;
        content.style.opacity = String(1 - Math.min(Math.abs(dampened) / window.innerWidth, 0.5));
    }, {passive: false});

    content.addEventListener("touchend", (event) => {
        if (startX === null) return;
        const touch = event.changedTouches[0];
        const deltaX = touch.clientX - startX;
        const direction = dragDirection;
        startX = null;
        dragDirection = null;

        if (!direction) return;

        const passed = Math.abs(deltaX) >= SWIPE_THRESHOLD_PX;

        if (!passed) {
            snapBack();
            return;
        }

        const target = targetFor(direction);
        sessionStorage.setItem(ENTRY_DIRECTION_KEY, direction === "left" ? "right" : "left");

        if (reducedMotion) {
            window.location.replace(target);
            return;
        }

        content.style.transition = `transform ${COMMIT_MS}ms ease-in, opacity ${COMMIT_MS}ms ease-in`;
        content.style.transform = `translateX(${direction === "left" ? "-100%" : "100%"})`;
        content.style.opacity = "0.3";
        setTimeout(() => {
            window.location.replace(target);
        }, COMMIT_MS);
    }, {passive: true});

    content.addEventListener("touchcancel", () => {
        if (startX === null) return;
        startX = null;
        const wasDragging = dragDirection;
        dragDirection = null;
        if (wasDragging) snapBack();
    }, {passive: true});
})();
