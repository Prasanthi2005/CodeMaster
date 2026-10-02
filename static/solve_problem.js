"use strict";

document.addEventListener("DOMContentLoaded", function() {

    const codeEditor = document.getElementById("codeEditor");
    const submitButton = document.getElementById("submitButton");
    const clearButton = document.getElementById("clearButton");
    const languageSelect = document.getElementById("languageSelect");
    const result = document.getElementById("result");
    const problemIdElement = document.getElementById("problemId");

    if (!codeEditor || !submitButton || !clearButton ||
        !languageSelect || !result || !problemIdElement) {

        console.error("Solve page elements missing.");
        return;
    }

    const problemId = problemIdElement.value;

    const placeholders = {
        python: "Write your Python solution here...",
        c: "Write your C solution here...",
        cpp: "Write your C++ solution here...",
        java: "Write your Java solution here..."
    };


    // =====================================================
    // BUTTON = NOT SOLVED BY DEFAULT
    // =====================================================

    function setNotSolvedButton() {

        submitButton.disabled = false;
        submitButton.classList.remove("solved");
        submitButton.textContent = "Submit Solution";
    }


    // =====================================================
    // BUTTON = SOLVED
    // =====================================================

    function setSolvedButton() {

        submitButton.disabled = true;
        submitButton.classList.add("solved");
        submitButton.textContent = "✓ Solved";
    }


    // =====================================================
    // PLACEHOLDER
    // =====================================================

    function updatePlaceholder() {

        const language = languageSelect.value;

        codeEditor.placeholder =
            placeholders[language] ||
            "Write your solution here...";
    }


    // =====================================================
    // LOAD CODE FROM DATABASE
    // =====================================================

    async function loadCodeFromDatabase() {

        const language = languageSelect.value;

        try {

            const response = await fetch(
                "/get_user_code/" +
                problemId +
                "?language=" +
                encodeURIComponent(language)
            );

            if (!response.ok) {

                console.error(
                    "Code load failed:",
                    response.status
                );

                codeEditor.value = "";
                return;
            }

            const data = await response.json();

            if (data.success) {

                codeEditor.value =
                    data.code || "";

                console.log(
                    "Loaded code:",
                    problemId,
                    language
                );

            } else {

                codeEditor.value = "";
            }

        } catch (error) {

            console.error(
                "Load code error:",
                error
            );

            codeEditor.value = "";
        }
    }


    // =====================================================
    // CHECK WHETHER CURRENT USER SOLVED THIS PROBLEM
    // =====================================================

    async function checkSolvedStatus() {

        try {

            const response = await fetch(
                "/check_solved/" + problemId
            );

            if (!response.ok) {

                setNotSolvedButton();
                return;
            }

            const data = await response.json();

            if (data.solved === true) {

                setSolvedButton();

            } else {

                setNotSolvedButton();
            }

        } catch (error) {

            console.error(
                "Solved status error:",
                error
            );

            setNotSolvedButton();
        }
    }


    // =====================================================
    // SAVE CODE
    // =====================================================

    async function saveCodeToDatabase() {

        const code = codeEditor.value;
        const language = languageSelect.value;

        try {

            const response = await fetch(
                "/save_user_code", {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        problem_id: problemId,
                        language: language,
                        code: code
                    })
                }
            );

            if (!response.ok) {

                console.error(
                    "Code save failed."
                );

                return;
            }

            console.log(
                "Code saved:",
                problemId,
                language
            );

        } catch (error) {

            console.error(
                "Save code error:",
                error
            );
        }
    }


    // =====================================================
    // CLEAR CODE
    // =====================================================

    async function clearCodeFromDatabase() {

        const language = languageSelect.value;

        try {

            const response = await fetch(
                "/clear_user_code", {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        problem_id: problemId,
                        language: language
                    })
                }
            );

            const data =
                await response.json();

            if (data.success) {

                console.log(
                    "Code deleted:",
                    problemId,
                    language
                );
            }

        } catch (error) {

            console.error(
                "Clear code error:",
                error
            );
        }
    }


    // =====================================================
    // LANGUAGE CHANGE
    // =====================================================

    languageSelect.addEventListener(
        "change",
        async function() {

            result.innerHTML = "";
            result.className = "result";

            updatePlaceholder();

            // Load code belonging to this user
            // and this language
            await loadCodeFromDatabase();

            // IMPORTANT:
            // Language change must NOT mark problem solved.
            // Ask server whether this problem is solved.
            await checkSolvedStatus();
        }
    );


    // =====================================================
    // AUTO SAVE WHILE TYPING
    // =====================================================

    let saveTimer = null;

    codeEditor.addEventListener(
        "input",
        function() {

            clearTimeout(saveTimer);

            saveTimer = setTimeout(
                function() {
                    saveCodeToDatabase();
                },
                700
            );
        }
    );


    // =====================================================
    // SUBMIT SOLUTION
    // =====================================================

    submitButton.addEventListener(
        "click",
        async function() {

            const code =
                codeEditor.value.trim();

            const language =
                languageSelect.value;


            // ---------------------------------------------
            // CODE EMPTY
            // ---------------------------------------------

            if (code === "") {

                result.innerHTML =
                    "❌ <strong>Please write your solution first.</strong>";

                result.className =
                    "result wrong";

                codeEditor.focus();

                return;
            }


            // ---------------------------------------------
            // SAVE CODE BEFORE RUN
            // ---------------------------------------------

            await saveCodeToDatabase();


            // ---------------------------------------------
            // RUNNING
            // ---------------------------------------------

            submitButton.disabled = true;
            submitButton.textContent = "Running...";

            result.innerHTML =
                "⏳ <strong>Running your " +
                language.toUpperCase() +
                " code...</strong>";

            result.className =
                "result info";


            try {

                const response =
                    await fetch(
                        "/submit_solution", {
                            method: "POST",

                            headers: {
                                "Content-Type": "application/json"
                            },

                            body: JSON.stringify({

                                problem_id: problemId,

                                code: code,

                                language: language
                            })
                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "SUBMIT RESPONSE:",
                    data
                );


                // =================================================
                // CORRECT
                // =================================================

                if (data.status === "correct") {

                    result.innerHTML =
                        "✅ <strong>Correct Answer!</strong>" +
                        "<br><br>" +
                        "Your " +
                        language.toUpperCase() +
                        " solution passed all test cases." +
                        "<br><br>" +
                        "<strong>Output:</strong>" +
                        "<pre>" +
                        escapeHtml(
                            data.output || "No output"
                        ) +
                        "</pre>";

                    result.className =
                        "result correct";


                    // Keep code in editor
                    codeEditor.value = code;


                    // Save permanently
                    await saveCodeToDatabase();


                    // ONLY NOW show solved
                    setSolvedButton();


                    console.log(
                        "Problem solved:",
                        problemId,
                        language
                    );

                    return;
                }


                // =================================================
                // WRONG
                // =================================================

                if (data.status === "wrong") {

                    const expected =
                        data.expected_output ||
                        data.expected ||
                        "No expected output";

                    const actual =
                        data.actual_output ||
                        data.output ||
                        "No output";


                    result.innerHTML =
                        "❌ <strong>Wrong Answer</strong>" +
                        "<br><br>" +
                        "<strong>Expected Output:</strong>" +
                        "<pre>" +
                        escapeHtml(expected) +
                        "</pre>" +
                        "<strong>Your Output:</strong>" +
                        "<pre>" +
                        escapeHtml(actual) +
                        "</pre>";

                    result.className =
                        "result wrong";


                    // Wrong answer is NOT solved
                    setNotSolvedButton();


                    // Keep user's code
                    await saveCodeToDatabase();

                    return;
                }


                // =================================================
                // COMPILATION / RUNTIME ERROR
                // =================================================

                if (data.status === "error") {

                    result.innerHTML =
                        "🔴 <strong>Compilation / Runtime Error</strong>" +
                        "<br><br>" +
                        "<pre>" +
                        escapeHtml(
                            data.error ||
                            data.message ||
                            "Unknown error"
                        ) +
                        "</pre>";

                    result.className =
                        "result error";


                    setNotSolvedButton();

                    await saveCodeToDatabase();

                    return;
                }


                // =================================================
                // TIMEOUT
                // =================================================

                if (data.status === "timeout") {

                    result.innerHTML =
                        "⏱️ <strong>Time Limit Exceeded</strong>" +
                        "<br><br>" +
                        "Your program took too long to execute.";

                    result.className =
                        "result error";


                    setNotSolvedButton();

                    await saveCodeToDatabase();

                    return;
                }


                // =================================================
                // LOGIN REQUIRED
                // =================================================

                if (data.status === "login_required") {

                    result.innerHTML =
                        "🔐 <strong>Please login first.</strong>";

                    result.className =
                        "result error";

                    setNotSolvedButton();

                    return;
                }


                // =================================================
                // SERVER ERROR
                // =================================================

                result.innerHTML =
                    "🔴 <strong>Server Error</strong>" +
                    "<br><br>" +
                    "<pre>" +
                    escapeHtml(
                        data.message ||
                        "Something went wrong."
                    ) +
                    "</pre>";

                result.className =
                    "result error";

                setNotSolvedButton();


                // Keep code
                await saveCodeToDatabase();

            } catch (error) {

                console.error(
                    "Submit error:",
                    error
                );

                result.innerHTML =
                    "🔴 <strong>Connection Error</strong>" +
                    "<br><br>" +
                    "<pre>" +
                    escapeHtml(
                        error.message
                    ) +
                    "</pre>";

                result.className =
                    "result error";

                setNotSolvedButton();

                await saveCodeToDatabase();
            }
        }
    );


    // =====================================================
    // CLEAR BUTTON
    // =====================================================

    clearButton.addEventListener(
        "click",
        async function() {

            codeEditor.value = "";

            await clearCodeFromDatabase();

            result.innerHTML = "";
            result.className = "result";

            /*
             * IMPORTANT:
             * Clear should NOT delete solved status.
             *
             * If user already solved the problem,
             * it remains solved.
             */

            await checkSolvedStatus();

            codeEditor.focus();
        }
    );


    // =====================================================
    // TAB SUPPORT
    // =====================================================

    codeEditor.addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Tab") {

                event.preventDefault();

                const start =
                    this.selectionStart;

                const end =
                    this.selectionEnd;


                this.value =
                    this.value.substring(
                        0,
                        start
                    ) +
                    "    " +
                    this.value.substring(
                        end
                    );


                this.selectionStart =
                    start + 4;

                this.selectionEnd =
                    start + 4;
            }
        }
    );


    // =====================================================
    // ESCAPE HTML
    // =====================================================

    function escapeHtml(text) {

        const div =
            document.createElement("div");

        div.textContent =
            String(text);

        return div.innerHTML;
    }


    // =====================================================
    // INITIAL PAGE LOAD
    // =====================================================

    async function initializePage() {

        updatePlaceholder();

        // First load current user's code
        await loadCodeFromDatabase();

        // Then check current user's solved status
        await checkSolvedStatus();

        console.log(
            "CodeMaster page initialized:",
            problemId,
            languageSelect.value
        );
    }


    initializePage();

});