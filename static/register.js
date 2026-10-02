/* =========================================================
   CODEMASTER REGISTER JAVASCRIPT
========================================================= */

document.addEventListener("DOMContentLoaded", function() {


    // =====================================================
    // GET ELEMENTS
    // =====================================================

    const form =
        document.getElementById("registerForm");

    const password =
        document.getElementById("password");

    const confirmPassword =
        document.getElementById("confirm_password");

    const imageInput =
        document.getElementById("profile_image");

    const registerButton =
        document.getElementById("registerButton");


    // =====================================================
    // PASSWORD SHOW / HIDE
    // =====================================================

    const toggleButtons =
        document.querySelectorAll(".toggle-password");


    toggleButtons.forEach(function(button) {

        button.addEventListener("click", function() {


            // Get target input

            const targetId =
                this.getAttribute("data-target");


            const targetInput =
                document.getElementById(targetId);


            // Get icon

            const icon =
                this.querySelector("i");


            // =================================================
            // SHOW PASSWORD
            // =================================================

            if (targetInput.type === "password") {

                targetInput.type = "text";

                icon.classList.remove(
                    "fa-eye"
                );

                icon.classList.add(
                    "fa-eye-slash"
                );

                this.setAttribute(
                    "aria-label",
                    "Hide password"
                );

            }


            // =================================================
            // HIDE PASSWORD
            // =================================================
            else {

                targetInput.type = "password";

                icon.classList.remove(
                    "fa-eye-slash"
                );

                icon.classList.add(
                    "fa-eye"
                );

                this.setAttribute(
                    "aria-label",
                    "Show password"
                );

            }

        });

    });



    // =====================================================
    // PROFILE IMAGE VALIDATION
    // =====================================================

    if (imageInput) {

        imageInput.addEventListener(
            "change",
            function() {


                const file =
                    this.files[0];


                if (!file) {
                    return;
                }


                // =================================================
                // IMAGE TYPE
                // =================================================

                if (!file.type.startsWith("image/")) {

                    alert(
                        "Please select a valid image file."
                    );

                    this.value = "";

                    return;
                }


                // =================================================
                // IMAGE SIZE - 5 MB
                // =================================================

                if (file.size > 5 * 1024 * 1024) {

                    alert(
                        "Profile picture must be less than 5 MB."
                    );

                    this.value = "";

                    return;
                }

            }
        );

    }



    // =====================================================
    // PASSWORD MATCH CHECK
    // =====================================================

    function checkPasswords() {


        if (!confirmPassword) {
            return;
        }


        if (confirmPassword.value === "") {

            confirmPassword.setCustomValidity("");

            return;
        }


        if (
            password.value !==
            confirmPassword.value
        ) {

            confirmPassword.setCustomValidity(
                "Passwords do not match."
            );

        } else {

            confirmPassword.setCustomValidity("");

        }

    }



    // Password typing

    if (password) {

        password.addEventListener(
            "input",
            checkPasswords
        );

    }


    // Confirm password typing

    if (confirmPassword) {

        confirmPassword.addEventListener(
            "input",
            checkPasswords
        );

    }



    // =====================================================
    // FORM SUBMIT
    // =====================================================

    if (form) {

        form.addEventListener(
            "submit",
            function(event) {


                checkPasswords();


                // =================================================
                // PASSWORD MISMATCH
                // =================================================

                if (
                    password.value !==
                    confirmPassword.value
                ) {

                    event.preventDefault();


                    alert(
                        "Password and Confirm Password must be the same."
                    );


                    confirmPassword.focus();


                    return;

                }


                // =================================================
                // DISABLE REGISTER BUTTON
                // =================================================

                if (registerButton) {

                    registerButton.disabled = true;


                    registerButton.innerHTML =
                        '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';

                }

            }
        );

    }

});