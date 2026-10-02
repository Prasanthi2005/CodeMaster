from flask_mail import Message
from app import mail

def send_otp_email(email, otp):
    msg = Message(
        subject="Your OTP Code",
        recipients=[email]
    )

    msg.body = f"Your OTP is: {otp}"

    mail.send(msg)