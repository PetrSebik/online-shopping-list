// Share the current recipe detail page — Web Share API on mobile (PWA has no
// URL bar to copy from), falling back to clipboard copy elsewhere.
// Delegated on document (not bound per-button) since the "Uvařeno"/tracking
// toggles swap this button's container via htmx, replacing the element.
document.addEventListener("click", (event) => {
    const btn = event.target.closest(".rc-share-btn");
    if (!btn) return;

    const title = btn.dataset.shareTitle || document.title;
    const url = window.location.href;

    if (navigator.share) {
        navigator.share({title, url}).catch(() => {
            // User cancelled the share sheet or it failed — nothing to do.
        });
        return;
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url)
            .then(() => showShareFeedback(btn, true))
            .catch(() => showShareFeedback(btn, false));
    }
});

function showShareFeedback(btn, success) {
    const original = btn.innerHTML;
    btn.innerHTML = success ? '<i class="bi bi-check-lg"></i>' : '<i class="bi bi-x-lg"></i>';
    btn.disabled = true;
    setTimeout(() => {
        btn.innerHTML = original;
        btn.disabled = false;
    }, 1500);
}
