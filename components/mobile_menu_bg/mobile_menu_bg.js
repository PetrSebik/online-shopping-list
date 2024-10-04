document.addEventListener("DOMContentLoaded", function () {
    var sideNav = document.getElementById("side_nav");
    var openBtn = document.getElementById("mobile-menu-open-btn");
    var closeBtn = document.getElementById("mobile-menu-close-btn");
    var overlay = document.getElementById("mobile-menu-overlay");

    openBtn.addEventListener("click", function () {
        sideNav.classList.add("active");
        overlay.style.display = "flex";
    });

    closeBtn.addEventListener("click", function () {
        sideNav.classList.remove("active");
        overlay.style.display = "none";
    });

    overlay.addEventListener("click", function () {
        sideNav.classList.remove("active");
        overlay.style.display = "none";
    });
});