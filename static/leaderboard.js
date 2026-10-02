/* =====================================================
   CODEMASTER LEADERBOARD JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", function() {


    // =====================================================
    // ELEMENTS
    // =====================================================

    const searchInput =
        document.getElementById("playerSearch");

    const table =
        document.getElementById("leaderboardTable");

    const noResults =
        document.getElementById("noResults");


    if (!searchInput || !table) {
        return;
    }


    // =====================================================
    // SEARCH PLAYER
    // =====================================================

    searchInput.addEventListener(
        "input",
        function() {

            const searchValue =
                this.value
                .toLowerCase()
                .trim();


            const rows =
                table.querySelectorAll(
                    "tbody tr"
                );


            let visibleRows = 0;


            rows.forEach(function(row) {

                const name =
                    row.dataset.name || "";

                const email =
                    row.dataset.email || "";

                const username =
                    row.dataset.username || "";


                const matches =
                    name.includes(searchValue) ||
                    email.includes(searchValue) ||
                    username.includes(searchValue);


                if (matches) {

                    row.style.display = "";

                    visibleRows++;

                } else {

                    row.style.display = "none";

                }

            });


            // =================================================
            // NO RESULT MESSAGE
            // =================================================

            if (visibleRows === 0) {

                noResults.style.display =
                    "block";

            } else {

                noResults.style.display =
                    "none";

            }

        }
    );


    // =====================================================
    // CLEAR SEARCH WITH ESC
    // =====================================================

    searchInput.addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Escape") {

                this.value = "";

                this.dispatchEvent(
                    new Event("input")
                );

            }

        }
    );


    // =====================================================
    // ADD ROW ANIMATION
    // =====================================================

    const rows =
        table.querySelectorAll(
            "tbody tr"
        );


    rows.forEach(function(row, index) {

        row.style.opacity = "0";

        row.style.transform =
            "translateY(8px)";


        setTimeout(function() {

            row.style.transition =
                "opacity 0.3s ease, transform 0.3s ease";

            row.style.opacity = "1";

            row.style.transform =
                "translateY(0)";

        }, index * 40);

    });


});