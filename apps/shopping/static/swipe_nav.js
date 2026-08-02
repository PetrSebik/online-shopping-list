// Flick-to-navigate between the shopping list and the recipe book.
// Swipe left on the shopping list -> last-viewed recipe page (remembered in
// localStorage). Swipe right on any recipe page -> shopping list. A short
// slide animation plays on both the outgoing and incoming page; the
// incoming page reads which direction to enter from out of sessionStorage
// (a one-shot flag set just before navigating away).
//
// Navigation uses location.replace(), not location.href/assign(), so a swipe
// swaps the current history entry instead of pushing a new one. Otherwise
// hopping back and forth (list -> detail -> swipe to shopping -> swipe back
// to detail) stacks duplicate entries and the OS back button lands on an
// intermediate stop instead of where you actually came from.
(function () {
    const SWIPE_THRESHOLD_PX = 70;
    const MAX_VERTICAL_RATIO = 0.6;
    const MAX_SWIPE_DURATION_MS = 800;
    const EXIT_ANIMATION_MS = 160;
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
    let startX = null;
    let startY = null;
    let startTime = null;

    content.addEventListener("touchstart", (event) => {
        if (event.touches.length !== 1) return;
        startX = event.touches[0].clientX;
        startY = event.touches[0].clientY;
        startTime = Date.now();
    }, {passive: true});

    content.addEventListener("touchend", (event) => {
        if (startX === null) return;
        const touch = event.changedTouches[0];
        const deltaX = touch.clientX - startX;
        const deltaY = touch.clientY - startY;
        const elapsed = Date.now() - startTime;
        startX = null;

        if (elapsed > MAX_SWIPE_DURATION_MS) return;
        if (Math.abs(deltaX) < SWIPE_THRESHOLD_PX) return;
        if (Math.abs(deltaY) > Math.abs(deltaX) * MAX_VERTICAL_RATIO) return;

        let target = null;
        let exitClass = null;
        let nextEntryDirection = null;

        if (isShoppingPage && deltaX < 0) {
            target = localStorage.getItem(LAST_RECIPE_URL_KEY) || "/recipe/list/";
            exitClass = "swipe-exit-left";
            nextEntryDirection = "right";
        } else if (isRecipePage && deltaX > 0) {
            target = "/shopping/list/";
            exitClass = "swipe-exit-right";
            nextEntryDirection = "left";
        }

        if (!target) return;

        sessionStorage.setItem(ENTRY_DIRECTION_KEY, nextEntryDirection);

        if (reducedMotion) {
            window.location.replace(target);
            return;
        }

        content.classList.add(exitClass);
        setTimeout(() => {
            window.location.replace(target);
        }, EXIT_ANIMATION_MS);
    }, {passive: true});
})();
