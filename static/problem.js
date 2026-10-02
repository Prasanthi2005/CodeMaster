// ==========================================
// problem.js
// CodeMaster - Problem Page JavaScript
// ==========================================

document.addEventListener("DOMContentLoaded", function() {

    // ===============================
    // Page Load Animation
    // ===============================

    const sections = document.querySelectorAll(".problem-card, .section");

    sections.forEach((section, index) => {

        section.style.opacity = "0";
        section.style.transform = "translateY(30px)";

        setTimeout(() => {

            section.style.transition = "0.6s ease";
            section.style.opacity = "1";
            section.style.transform = "translateY(0)";

        }, index * 150);

    });


    // ===============================
    // Button Hover Effect
    // ===============================

    const buttons = document.querySelectorAll(".btn");

    buttons.forEach(button => {

        button.addEventListener("mouseenter", function() {
            button.style.transform = "scale(1.05)";
        });

        button.addEventListener("mouseleave", function() {
            button.style.transform = "scale(1)";
        });

    });


    // ===============================
    // Copy Sample Code
    // ===============================

    const codeBlocks = document.querySelectorAll("pre");

    codeBlocks.forEach(codeBlock => {

        codeBlock.style.cursor = "pointer";
        codeBlock.title = "Click to copy sample";

        codeBlock.addEventListener("click", function() {

            navigator.clipboard.writeText(codeBlock.innerText)
                .then(() => {
                    alert("✅ Sample copied to clipboard!");
                })
                .catch(error => {
                    console.error("Copy failed:", error);
                });

        });

    });


    // ===============================
    // Solve Button
    // ===============================

    const solveBtn = document.querySelector(".btn");

    if (solveBtn) {

        solveBtn.addEventListener("click", function() {

            console.log("Opening Code Editor...");

        });

    }


    // ===============================
    // Submit Solution
    // ===============================

    const submitBtn =
        document.querySelector("#submit-solution") ||
        document.querySelector("#submitBtn") ||
        document.querySelector(".submit-btn");

    if (submitBtn) {

        submitBtn.addEventListener("click", async function() {

            try {

                // --------------------------------
                // Get Editor Code
                // --------------------------------

                let code = "";

                // Monaco Editor
                if (typeof editor !== "undefined" && editor) {
                    code = editor.getValue();
                }

                // Alternative Monaco variable
                else if (
                    typeof monacoEditor !== "undefined" &&
                    monacoEditor
                ) {
                    code = monacoEditor.getValue();
                }

                // Textarea fallback
                else {

                    const textarea =
                        document.querySelector("#code-editor") ||
                        document.querySelector("#editor") ||
                        document.querySelector("textarea");

                    if (textarea) {
                        code = textarea.value;
                    }

                }


                // --------------------------------
                // Check Code
                // --------------------------------

                if (!code.trim()) {

                    alert("⚠️ Please enter your code first.");

                    return;
                }


                // --------------------------------
                // Get Problem ID
                // --------------------------------

                const pathParts =
                    window.location.pathname
                    .split("/")
                    .filter(Boolean);

                const problemId =
                    pathParts[pathParts.length - 1];


                console.log("Problem ID:", problemId);
                console.log("Submitting code...");


                // --------------------------------
                // Disable Button
                // --------------------------------

                submitBtn.disabled = true;
                submitBtn.innerText = "⏳ Running...";


                // --------------------------------
                // Send Code to Flask
                // --------------------------------

                const response = await fetch("/submit_solution", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        problem_id: problemId,

                        code: code

                    })

                });


                // --------------------------------
                // Check Response
                // --------------------------------

                if (!response.ok) {

                    throw new Error(
                        "Server error: " + response.status
                    );

                }


                const data = await response.json();

                console.log("Server Response:", data);


                // --------------------------------
                // Output Box
                // --------------------------------

                const outputBox =
                    document.querySelector("#output");


                if (outputBox) {

                    if (data.output !== undefined &&
                        data.output !== null) {

                        outputBox.textContent =
                            String(data.output);

                    } else {

                        outputBox.textContent =
                            "No output.";

                    }

                }


                // --------------------------------
                // Success Message
                // --------------------------------

                const successMessage =
                    document.querySelector("#success-message");


                if (data.success === true) {

                    if (successMessage) {

                        successMessage.style.display = "block";

                        successMessage.innerHTML = `
                            <strong>✓ Correct Answer!</strong>
                            <br>
                            Your solution passed all test cases.
                        `;

                    }

                    submitBtn.innerText = "✓ Solved";

                }


                // --------------------------------
                // Wrong Answer
                // --------------------------------
                else {

                    if (successMessage) {

                        successMessage.style.display = "block";

                        successMessage.innerHTML = `
                            <strong>❌ Wrong Answer</strong>
                            <br>
                            Please check your solution and try again.
                        `;

                    }

                    submitBtn.innerText = "Run Again";

                }

            }


            // --------------------------------
            // Error Handling
            // --------------------------------
            catch (error) {

                console.error(
                    "Submission Error:",
                    error
                );


                const outputBox =
                    document.querySelector("#output");


                if (outputBox) {

                    outputBox.textContent =
                        "Error: " + error.message;

                }


                alert(
                    "❌ Unable to submit solution. Check the console."
                );

            }


            // --------------------------------
            // Enable Button
            // --------------------------------
            finally {

                submitBtn.disabled = false;

            }

        });

    }


    // ===============================
    // Clear Output
    // ===============================

    const clearBtn =
        document.querySelector("#clear-btn") ||
        document.querySelector("#clearBtn");

    if (clearBtn) {

        clearBtn.addEventListener("click", function() {

            const outputBox =
                document.querySelector("#output");

            if (outputBox) {
                outputBox.textContent = "";
            }

            const successMessage =
                document.querySelector("#success-message");

            if (successMessage) {
                successMessage.style.display = "none";
            }

            console.log("Output cleared.");

        });

    }


    // ===============================
    // Keyboard Shortcut
    // Ctrl + Enter
    // ===============================

    document.addEventListener("keydown", function(event) {

        if (event.ctrlKey && event.key === "Enter") {

            event.preventDefault();

            if (submitBtn) {

                submitBtn.click();

            } else {

                console.log(
                    "Submit button not found."
                );

            }

        }

    });


    // ===============================
    // Welcome Message
    // ===============================

    console.log(
        "Welcome to the CodeMaster Problem Page"
    );

});