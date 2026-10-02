// =========================================================
// CodeMaster - Problems JavaScript
// problems.js
// =========================================================

"use strict";


document.addEventListener(
    "DOMContentLoaded",
    function() {


        // =====================================================
        // ELEMENTS
        // =====================================================

        const searchInput =
            document.getElementById("searchInput");


        const difficulty =
            document.getElementById("difficulty");


        const category =
            document.getElementById("category");


        const table =
            document.getElementById("problemTable");


        const problemCount =
            document.getElementById("problemCount");


        if (!searchInput ||
            !difficulty ||
            !category ||
            !table
        ) {
            return;
        }


        // =====================================================
        // GET PROBLEM ROWS
        // =====================================================

        const rows =
            Array.from(
                table.querySelectorAll("tr")
            );


        // =====================================================
        // FILTER FUNCTION
        // =====================================================

        function filterProblems() {


            const searchValue =
                searchInput.value
                .toLowerCase()
                .trim();


            const difficultyValue =
                difficulty.value;


            const categoryValue =
                category.value;


            let visibleCount = 0;


            rows.forEach(
                function(row) {


                    const rowDifficulty =
                        row.dataset.difficulty || "";


                    const rowCategory =
                        row.dataset.category || "";


                    const rowSearch =
                        (
                            row.dataset.search ||
                            ""
                        ).toLowerCase();


                    // =========================================
                    // SEARCH
                    // =========================================

                    const searchMatch =
                        rowSearch.includes(
                            searchValue
                        );


                    // =========================================
                    // DIFFICULTY
                    // =========================================

                    const difficultyMatch =
                        difficultyValue === "All" ||
                        rowDifficulty === difficultyValue;


                    // =========================================
                    // CATEGORY
                    // =========================================

                    const categoryMatch =
                        categoryValue === "All" ||
                        rowCategory === categoryValue;


                    // =========================================
                    // FINAL RESULT
                    // =========================================

                    if (
                        searchMatch &&
                        difficultyMatch &&
                        categoryMatch
                    ) {

                        row.style.display = "";

                        visibleCount++;

                    } else {

                        row.style.display = "none";

                    }

                }
            );


            // =================================================
            // UPDATE COUNT
            // =================================================

            if (problemCount) {

                problemCount.textContent =
                    visibleCount +
                    (
                        visibleCount === 1 ?
                        " Problem" :
                        " Problems"
                    );

            }


            // =================================================
            // NO RESULTS
            // =================================================

            showNoResults(
                visibleCount === 0
            );

        }


        // =====================================================
        // NO RESULTS MESSAGE
        // =====================================================

        function showNoResults(show) {


            let existing =
                document.getElementById(
                    "noResults"
                );


            if (show) {

                if (!existing) {

                    existing =
                        document.createElement("tr");

                    existing.id =
                        "noResults";

                    existing.innerHTML = `
                        <td colspan="6">
                            <div class="no-results">
                                <i class="fa-solid fa-magnifying-glass"></i>
                                <strong>No problems found</strong>
                                <p>
                                    Try another search or filter.
                                </p>
                            </div>
                        </td>
                    `;

                    table.appendChild(existing);

                }

            } else {

                if (existing) {

                    existing.remove();

                }

            }

        }


        // =====================================================
        // SEARCH EVENT
        // =====================================================

        searchInput.addEventListener(
            "input",
            filterProblems
        );


        // =====================================================
        // DIFFICULTY EVENT
        // =====================================================

        difficulty.addEventListener(
            "change",
            filterProblems
        );


        // =====================================================
        // CATEGORY EVENT
        // =====================================================

        category.addEventListener(
            "change",
            filterProblems
        );


        // =====================================================
        // CLEAR SEARCH WITH ESC
        // =====================================================

        searchInput.addEventListener(
            "keydown",
            function(event) {

                if (
                    event.key === "Escape"
                ) {

                    searchInput.value = "";

                    filterProblems();

                    searchInput.blur();

                }

            }
        );


        // =====================================================
        // SOLVE BUTTON ANIMATION
        // =====================================================

        const solveButtons =
            document.querySelectorAll(
                ".solve-btn"
            );


        solveButtons.forEach(
            function(button) {

                button.addEventListener(
                    "click",
                    function() {

                        button.style.opacity =
                            "0.75";

                        button.style.transform =
                            "scale(0.97)";

                    }
                );

            }
        );


        // =====================================================
        // INITIAL FILTER
        // =====================================================

        filterProblems();


    }
);