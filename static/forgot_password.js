// CodeMaster Forgot Password JavaScript


document.addEventListener("DOMContentLoaded", function() {


    const form = document.querySelector("form");

    const emailInput = document.getElementById("email");

    const button = document.querySelector("button");



    form.addEventListener("submit", function(event) {


        let email = emailInput.value.trim();



        // Empty check

        if (email === "") {

            event.preventDefault();

            alert("Please enter your Gmail address");

            return false;

        }



        // Gmail validation

        let gmailPattern =
            /^[a-zA-Z0-9._%+-]+@gmail\.com$/;



        if (!gmailPattern.test(email)) {


            event.preventDefault();


            alert("Please enter a valid Gmail address");


            return false;


        }



        // Loading effect

        button.innerHTML = "Sending OTP...";


        button.disabled = true;



    });



});