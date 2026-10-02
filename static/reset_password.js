document.addEventListener("DOMContentLoaded", function() {

    const codeEditor = document.getElementById("codeEditor");
    const submitButton = document.getElementById("submitButton");
    const clearButton = document.getElementById("clearButton");
    const languageSelect = document.getElementById("languageSelect");
    const result = document.getElementById("result");

    const problemId = window.PROBLEM_ID;


    const placeholders = {
        python: "Write your Python solution here...",
        c: "Write your C solution here...",
        cpp: "Write your C++ solution here...",
        java: "Write your Java solution here..."
    };


    /* ================================
       LANGUAGE CHANGE
    ================================= */

    languageSelect.addEventListener("change", function() {

        const language = this.value;

        codeEditor.placeholder = placeholders[language];

        codeEditor.value = "";

        result.textContent = "";

        result.className = "result";

    });


    /* ================================
       SUBMIT SOLUTION
    ================================= */

    submitButton.addEventListener("click", async function() {

        const code = codeEditor.value.trim();

        const language = languageSelect.value;


        if (code === "") {

            result.textContent =
                "❌ Please write your solution first.";

            result.className = "result wrong";

            codeEditor.focus();

            return;
        }


        submitButton.disabled = true;

        submitButton.textContent = "Checking...";


        result.textContent =
            "⏳ Running your code against test cases...";

        result.className = "result info";


        try {

            const response = await fetch(
                `/submit_solution/${problemId}`, {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        code: code,
                        language: language
                    })
                }
            );


            const data = await response.json();


            if (data.status === "correct") {

                result.textContent =
                    "✔ Correct Answer! All test cases passed.";

                result.className = "result correct";

            } else {

                result.textContent =
                    "❌ Wrong Answer! " +
                    (data.message || "Some test cases failed.");

                result.className = "result wrong";

            }


        } catch (error) {

            result.textContent =
                "❌ Unable to submit solution. Please try again.";

            result.className = "result wrong";

            console.error(error);

        }


        submitButton.disabled = false;

        submitButton.textContent = "Submit Solution";

    });


    /* ================================
       CLEAR BUTTON
    ================================= */

    clearButton.addEventListener("click", function() {

        codeEditor.value = "";

        result.textContent = "";

        result.className = "result";

        codeEditor.focus();

    });


    /* ================================
       TAB SUPPORT
    ================================= */

    codeEditor.addEventListener("keydown", function(event) {

        if (event.key === "Tab") {

            event.preventDefault();

            const start = this.selectionStart;
            const end = this.selectionEnd;

            this.value =
                this.value.substring(0, start) +
                "    " +
                this.value.substring(end);

            this.selectionStart = start + 4;
            this.selectionEnd = start + 4;
        }

    });


    codeEditor.placeholder =
        placeholders[languageSelect.value];

});