// ============================
// script.js
// ============================

// Typing Animation

const words = [
    "with AI",
    "for Placements",
    "Like LeetCode",
    "Like HackerRank"
];

let wordIndex = 0;
let charIndex = 0;

const typing = document.getElementById("typing");

function typeEffect() {

    if (charIndex < words[wordIndex].length) {

        typing.innerHTML += words[wordIndex].charAt(charIndex);

        charIndex++;

        setTimeout(typeEffect, 100);

    } else {

        setTimeout(eraseEffect, 1500);

    }

}

function eraseEffect() {

    if (charIndex > 0) {

        typing.innerHTML = words[wordIndex].substring(0, charIndex - 1);

        charIndex--;

        setTimeout(eraseEffect, 50);

    } else {

        wordIndex++;

        if (wordIndex >= words.length) {

            wordIndex = 0;

        }

        setTimeout(typeEffect, 300);

    }

}

typeEffect();


// Feature Card Animation

const cards = document.querySelectorAll(".feature-box");

window.addEventListener("scroll", () => {

    cards.forEach(card => {

        let position = card.getBoundingClientRect().top;

        let screen = window.innerHeight;

        if (position < screen - 100) {

            card.style.opacity = "1";

            card.style.transform = "translateY(0px)";

        }

    });

});
/* =========================================================
   MOBILE NAVIGATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", function() {

    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const navLinks = document.getElementById("navLinks");

    if (!mobileMenuBtn || !navLinks) {
        return;
    }

    const menuIcon = mobileMenuBtn.querySelector("i");

    function openMobileMenu() {
        navLinks.classList.add("mobile-open");

        mobileMenuBtn.setAttribute("aria-expanded", "true");
        mobileMenuBtn.setAttribute(
            "aria-label",
            "Close navigation menu"
        );

        if (menuIcon) {
            menuIcon.classList.remove("fa-bars");
            menuIcon.classList.add("fa-xmark");
        }
    }

    function closeMobileMenu() {
        navLinks.classList.remove("mobile-open");

        mobileMenuBtn.setAttribute("aria-expanded", "false");
        mobileMenuBtn.setAttribute(
            "aria-label",
            "Open navigation menu"
        );

        if (menuIcon) {
            menuIcon.classList.remove("fa-xmark");
            menuIcon.classList.add("fa-bars");
        }
    }

    function toggleMobileMenu() {
        if (navLinks.classList.contains("mobile-open")) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }

    /* Hamburger click */
    mobileMenuBtn.addEventListener("click", function(event) {
        event.stopPropagation();
        toggleMobileMenu();
    });


    /* Close after clicking a navigation link */
    navLinks.querySelectorAll("a").forEach(function(link) {

        link.addEventListener("click", function() {

            if (window.innerWidth <= 768) {
                closeMobileMenu();
            }

        });

    });


    /* Close when clicking outside */
    document.addEventListener("click", function(event) {

        if (window.innerWidth > 768) {
            return;
        }

        const clickedInsideMenu =
            navLinks.contains(event.target);

        const clickedMenuButton =
            mobileMenuBtn.contains(event.target);

        if (!clickedInsideMenu && !clickedMenuButton) {
            closeMobileMenu();
        }

    });


    /* Close menu with Escape key */
    document.addEventListener("keydown", function(event) {

        if (event.key === "Escape") {
            closeMobileMenu();
        }

    });


    /* Reset mobile menu when resizing to desktop */
    window.addEventListener("resize", function() {

        if (window.innerWidth > 768) {
            closeMobileMenu();
        }

    });

});