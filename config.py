# ==========================================
# config.py
# CodeMaster Configuration File
# ==========================================

import os
from dotenv import load_dotenv


# ==========================================
# LOAD .ENV
# ==========================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)


class Config:

    # ==========================================
    # SECRET KEY
    # ==========================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "codemaster_super_secret_key_2026"
    )

    SESSION_COOKIE_NAME = "codemaster_login"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


    # ==========================================
    # GOOGLE OAUTH
    # ==========================================

   GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
   GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


    # ==========================================
    # GMAIL SMTP
    # ==========================================

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            "587"
        )
    )

    MAIL_USE_TLS = (
        os.getenv(
            "MAIL_USE_TLS",
            "True"
        ).lower() == "true"
    )

    MAIL_USE_SSL = (
        os.getenv(
            "MAIL_USE_SSL",
            "False"
        ).lower() == "true"
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        ""
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
        ""
    )

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        MAIL_USERNAME
    )


    # ==========================================
    # SQLITE DATABASE
    # ==========================================

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///"
        + os.path.join(
            BASE_DIR,
            "database.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ==========================================
    # UPLOAD FOLDER
    # ==========================================

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads"
    )


    # ==========================================
    # CERTIFICATE FOLDER
    # ==========================================

    CERTIFICATE_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "certificates"
    )


    # ==========================================
    # ALLOWED FILE TYPES
    # ==========================================

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "docx"
    }


    # ==========================================
    # MAXIMUM UPLOAD SIZE
    # ==========================================

    MAX_CONTENT_LENGTH = (
        16 * 1024 * 1024
    )


    # ==========================================
    # JUDGE0 API
    # ==========================================

    JUDGE0_API_URL = (
        "https://judge0-ce.p.rapidapi.com/submissions"
    )

    JUDGE0_API_KEY = os.getenv(
        "JUDGE0_API_KEY",
        ""
    )


    # ==========================================
    # GEMINI API
    # ==========================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        ""
    )


    # ==========================================
    # ADMIN CREDENTIALS
    # ==========================================

    ADMIN_EMAIL = "admin@codemaster.com"

    ADMIN_PASSWORD = "admin123"


    # ==========================================
    # DEFAULT LANGUAGE
    # ==========================================

    DEFAULT_LANGUAGE = "Python"


    # ==========================================
    # CONTEST SETTINGS
    # ==========================================

    MAX_CONTEST_TIME = 180

    MAX_PROBLEMS_PER_CONTEST = 10


    # ==========================================
    # LEADERBOARD
    # ==========================================

    DEFAULT_RATING = 1000

    DEFAULT_SCORE = 0


    # ==========================================
    # CERTIFICATE
    # ==========================================

    ORGANIZATION_NAME = "CodeMaster"

    CERTIFICATE_SIGNATURE = "CodeMaster Team"


    # ==========================================
    # FLASK DEBUG
    # ==========================================

    DEBUG = True

    TESTING = False