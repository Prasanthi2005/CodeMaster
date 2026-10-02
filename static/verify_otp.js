document.addEventListener('DOMContentLoaded', function() {

    const inputs = document.querySelectorAll('.otp-input');
    const finalOTP = document.getElementById('finalOTP');
    const resendBtn = document.getElementById('resendBtn');
    const timer = document.getElementById('timer');
    const form = document.getElementById('otpForm');

    // NEW: Verify button
    const verifyBtn = document.getElementById('verifyBtn');

    let countdown;
    let time = 60;
    let isExpired = false;

    // Enable all OTP boxes immediately
    inputs.forEach((input) => {
        input.disabled = false;
        input.readOnly = false;
        input.style.pointerEvents = 'auto';
        input.style.cursor = 'text';
    });

    function combineOTP() {
        let otp = '';
        inputs.forEach(input => otp += input.value);
        finalOTP.value = otp;
    }

    // Typing support
    inputs.forEach((input, index) => {

        input.addEventListener('input', function(e) {

            e.target.value = e.target.value.replace(/[^0-9]/g, '');

            if (e.target.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            combineOTP();
        });

        input.addEventListener('keydown', function(e) {

            if (e.key === 'Backspace' && input.value === '' && index > 0) {
                inputs[index - 1].focus();
            }
        });

        // Click focus fix
        input.addEventListener('click', function() {
            input.focus();
        });
    });

    // Timer
    function startTimer() {

        clearInterval(countdown);

        time = 60;
        isExpired = false;

        timer.textContent = time;

        resendBtn.disabled = true;

        // Enable verify button again
        verifyBtn.disabled = false;
        verifyBtn.style.opacity = '1';

        countdown = setInterval(function() {

            time--;
            timer.textContent = time;

            if (time <= 0) {

                clearInterval(countdown);

                timer.textContent = 'Expired';

                resendBtn.disabled = false;

                // NEW: Expire OTP
                isExpired = true;

                // Disable verify button
                verifyBtn.disabled = true;
                verifyBtn.style.opacity = '0.6';
            }

        }, 1000);
    }

    // Resend OTP
    resendBtn.addEventListener('click', function() {

        fetch('/resend-otp', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {

                alert(data.message || 'OTP resent successfully');

                inputs.forEach(input => {
                    input.value = '';
                    input.disabled = false;
                    input.readOnly = false;
                    input.style.pointerEvents = 'auto';
                });

                inputs[0].focus();

                combineOTP();

                // Restart timer
                startTimer();
            })
            .catch(error => {
                console.error(error);
                alert('Failed to resend OTP');
            });
    });

    // Verify submit
    form.addEventListener('submit', function(e) {

        combineOTP();

        // NEW: Stop submit if expired
        if (isExpired) {
            e.preventDefault();
            alert('OTP expired. Please resend OTP.');
            return;
        }

        if (finalOTP.value.length !== 6) {
            e.preventDefault();
            alert('Please enter 6 digit OTP');
        }
    });

    startTimer();

    // Focus first box automatically
    inputs[0].focus();
});