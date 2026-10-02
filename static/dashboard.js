"use strict";

document.addEventListener("DOMContentLoaded", function() {

    /* =====================================================
       LIVE CLOCK
    ====================================================== */

    const currentTime = document.getElementById("currentTime");

    function updateClock() {

        if (!currentTime) {
            return;
        }

        const now = new Date();

        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, "0");
        const seconds = String(now.getSeconds()).padStart(2, "0");

        const period = hours >= 12 ? "PM" : "AM";

        hours = hours % 12;

        if (hours === 0) {
            hours = 12;
        }

        hours = String(hours).padStart(2, "0");

        currentTime.textContent =
            `${hours}:${minutes}:${seconds} ${period}`;
    }

    updateClock();

    setInterval(updateClock, 1000);


    /* =====================================================
       ANIMATED COUNTERS
    ====================================================== */

    const counters = document.querySelectorAll(".counter");

    counters.forEach(function(counter) {

        const target =
            parseInt(counter.getAttribute("data-value")) || 0;

        let current = 0;

        const duration = 1000;

        const stepTime =
            Math.max(Math.floor(duration / Math.max(target, 1)), 15);

        const timer = setInterval(function() {

            current++;

            if (current >= target) {

                current = target;

                clearInterval(timer);
            }

            counter.textContent =
                current.toLocaleString();

        }, stepTime);

    });


    /* =====================================================
       PROGRESS
    ====================================================== */

    const progressFill =
        document.getElementById("progressFill");

    const progressPercent =
        document.getElementById("progressPercent");

    if (progressFill && progressPercent) {

        const solvedElement =
            document.querySelector(
                '.counter[data-value]'
            );

        let solved = 0;

        if (solvedElement) {

            solved =
                parseInt(
                    solvedElement.getAttribute("data-value")
                ) || 0;
        }

        /*
           Progress is visual only.
           Maximum shown as 100 solved problems.
        */

        let percentage =
            Math.min((solved / 100) * 100, 100);

        percentage =
            Math.round(percentage);

        setTimeout(function() {

            progressFill.style.width =
                percentage + "%";

            progressPercent.textContent =
                percentage + "%";

        }, 250);
    }


    /* =====================================================
       ACTION CARD RIPPLE EFFECT
    ====================================================== */

    const actionCards =
        document.querySelectorAll(".action-card");

    actionCards.forEach(function(card) {

        card.addEventListener("click", function() {

            card.style.transform =
                "scale(0.98)";

            setTimeout(function() {

                card.style.transform = "";

            }, 120);

        });

    });


    /* =====================================================
       ACTIVE SIDEBAR
    ====================================================== */

    const currentPath =
        window.location.pathname;

    const navItems =
        document.querySelectorAll(".nav-item");

    navItems.forEach(function(item) {

        const href =
            item.getAttribute("href");

        if (
            href &&
            href === currentPath &&
            !item.classList.contains("logout")
        ) {

            navItems.forEach(function(nav) {
                nav.classList.remove("active");
            });

            item.classList.add("active");
        }

    });


    /* =====================================================
       PAGE LOAD ANIMATION
    ====================================================== */

    const cards =
        document.querySelectorAll(
            ".stat-card, .action-card, .dashboard-card"
        );

    cards.forEach(function(card, index) {

        card.style.opacity = "0";

        card.style.transform =
            "translateY(12px)";

        setTimeout(function() {

            card.style.transition =
                "opacity .45s ease, transform .45s ease";

            card.style.opacity = "1";

            card.style.transform =
                "translateY(0)";

        }, 80 + (index * 60));

    });

});