// =========================================================
// CodeMaster Login JavaScript
// login.js
// =========================================================

"use strict";

document.addEventListener("DOMContentLoaded", function() {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const form =
        document.getElementById("loginForm");

    const email =
        document.getElementById("email");

    const password =
        document.getElementById("password");

    const showPassword =
        document.getElementById("showPassword");

    const loginButton =
        document.getElementById("loginButton");


    // =====================================================
    // PASSWORD SHOW / HIDE
    // =====================================================

    if (showPassword && password) {

        showPassword.addEventListener(
            "click",
            function() {

                if (password.type === "password") {

                    password.type = "text";

                    showPassword.innerHTML =
                        '<i class="fa-solid fa-eye-slash"></i>';

                    showPassword.setAttribute(
                        "aria-label",
                        "Hide password"
                    );

                    showPassword.setAttribute(
                        "title",
                        "Hide password"
                    );

                } else {

                    password.type = "password";

                    showPassword.innerHTML =
                        '<i class="fa-solid fa-eye"></i>';

                    showPassword.setAttribute(
                        "aria-label",
                        "Show password"
                    );

                    showPassword.setAttribute(
                        "title",
                        "Show password"
                    );

                }

            }
        );

    }


    // =====================================================
    // EMAIL VALIDATION
    // =====================================================

    function isValidEmail(value) {

        const pattern =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        return pattern.test(value);

    }


    // =====================================================
    // FORM SUBMIT
    // =====================================================

    if (form) {

        form.addEventListener(
            "submit",
            function(event) {

                const emailValue =
                    email.value.trim();

                const passwordValue =
                    password.value;


                // ==========================================
                // EMAIL EMPTY
                // ==========================================

                if (!emailValue) {

                    event.preventDefault();

                    alert(
                        "Please enter your email."
                    );

                    email.focus();

                    return;

                }


                // ==========================================
                // INVALID EMAIL
                // ==========================================

                if (!isValidEmail(emailValue)) {

                    event.preventDefault();

                    alert(
                        "Please enter a valid email address."
                    );

                    email.focus();

                    return;

                }


                // ==========================================
                // PASSWORD EMPTY
                // ==========================================

                if (!passwordValue) {

                    event.preventDefault();

                    alert(
                        "Please enter your password."
                    );

                    password.focus();

                    return;

                }


                // ==========================================
                // PASSWORD LENGTH
                // ==========================================

                if (passwordValue.length < 6) {

                    event.preventDefault();

                    alert(
                        "Password must contain at least 6 characters."
                    );

                    password.focus();

                    return;

                }


                // ==========================================
                // VALID LOGIN
                // ==========================================

                // IMPORTANT:
                // ikkada preventDefault() pettakudadhu.
                //
                // Browser normal POST request chestundi:
                //
                // /login
                //
                // Flask login route credentials verify chesi
                // direct ga /dashboard ki redirect chestundi.


                if (loginButton) {

                    loginButton.disabled = true;

                    loginButton.classList.add(
                        "loading"
                    );

                }

            }
        );

    }


    // =====================================================
    // INPUT FOCUS EFFECT
    // =====================================================

    const inputs =
        document.querySelectorAll(
            ".login-form input"
        );


    inputs.forEach(function(input) {

        input.addEventListener(
            "focus",
            function() {

                input.parentElement.classList.add(
                    "active"
                );

            }
        );


        input.addEventListener(
            "blur",
            function() {

                input.parentElement.classList.remove(
                    "active"
                );

            }
        );

    });


    // =====================================================
    // CAPS LOCK WARNING
    // =====================================================

    if (password) {

        password.addEventListener(
            "keyup",
            function(event) {

                if (event.getModifierState &&
                    event.getModifierState("CapsLock")) {

                    password.title =
                        "Caps Lock is ON";

                } else {

                    password.title =
                        "";

                }

            }
        );

    }


    // =====================================================
    // AUTO FOCUS EMAIL
    // =====================================================

    if (email) {

        email.focus();

    }

});