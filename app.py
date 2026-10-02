# ==========================================
# app.py
# CodeMaster - Flask Application
# Part 1
# ==========================================

from unittest import result

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    url_for,
    flash,
    session,
    jsonify
)

import sqlite3
from reportlab.pdfbase.pdfmetrics import stringWidth
import io
import sys
from flask import redirect
from reportlab.lib.units import mm
from datetime import datetime, timedelta, timezone
import shutil
import os
import stat
import time
import re
import subprocess
import tempfile
import sqlite3
import uuid
import random
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from database import init_db, seed_problems
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from flask import session
import smtplib
import ssl
from email.message import EmailMessage
from database import get_db
from werkzeug.security import generate_password_hash
import tempfile
from authlib.integrations.flask_client import OAuth

from flask_mail import Mail, Message
from flask import Flask, request, jsonify, session




from config import Config
from authlib.integrations.flask_client import OAuth


# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)
# =========================================================
# CODE EXECUTION FOLDER
# =========================================================

RUN_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "code_runs"
)

os.makedirs(
    RUN_FOLDER,
    exist_ok=True
)
init_db()
seed_problems()

app.config.from_object(Config)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "prasanthia06@gmail.com"
app.config["MAIL_PASSWORD"] = "rabdlglgyqsxymfp"

mail = Mail(app)



# =========================================================
# CONTEST DATABASE
# =========================================================
# =========================================================
# CREATE RECURRING CONTESTS
# =========================================================


# =========================================================
# AUTOMATIC CONTEST CREATION
# =========================================================


def send_otp_email(email, otp):

    msg = Message(
        subject="CodeMaster Password Reset OTP",
        recipients=[email]
    )

    msg.body = f"""
Hello,

Your CodeMaster OTP is:

{otp}

This OTP is valid for 10 minutes.

Do not share this OTP with anyone.

Thanks,
CodeMaster Team
"""

    mail.send(msg)
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
) 

DATABASE = "database.db"


# ==========================================
# Database Connection
# ==========================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
# ============================================================
# LANGUAGE NORMALIZER
# ============================================================

def normalize_language(language):
    language = (language or "python").strip().lower()

    if language in ["py", "python"]:
        return "python"

    if language in ["c++", "cpp"]:
        return "cpp"

    if language in ["java"]:
        return "java"

    if language in ["c"]:
        return "c"

    return language


# ============================================================
# SAVE SOLVED PROBLEM
# ============================================================

def save_solved_problem(user_id, problem_id, language):

    language = normalize_language(language)
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO user_problem_progress
            (user_id, problem_id, language)
            VALUES (?, ?, ?)
        """, (user_id, problem_id, language))
        db.commit()
        return cursor.rowcount > 0
    finally:
        db.close()


# ============================================================
# GET USER PROGRESS
# ============================================================

def get_user_progress(user_id):

    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT language, COUNT(DISTINCT problem_id) AS solved_count
            FROM user_problem_progress
            WHERE user_id = ?
            GROUP BY language
        """, (user_id,))

        rows = cursor.fetchall()
        progress = {"python": 0, "java": 0, "cpp": 0, "c": 0}

        for row in rows:
            language = normalize_language(row["language"])
            if language in progress:
                progress[language] = row["solved_count"]

        cursor.execute("""
            SELECT COUNT(DISTINCT problem_id)
            FROM user_problem_progress
            WHERE user_id = ?
        """, (user_id,))

        total_solved = cursor.fetchone()[0]
        return progress, total_solved
    finally:
        db.close()


# ==========================================
# Create Users Table
# ==========================================

def create_tables():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        fullname TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        phone TEXT,

        username TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        language TEXT,

        score INTEGER DEFAULT 0,

        solved INTEGER DEFAULT 0,

        rating INTEGER DEFAULT 0

    )
    """)


    # =========================
    # USERS TABLE
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            language TEXT,
            score INTEGER DEFAULT 0,
            solved INTEGER DEFAULT 0,
            rating INTEGER DEFAULT 1000
        )
    """)

    conn.commit()
    conn.close()
def create_contest_tables():

    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS contest_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contest_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(contest_id, user_id)
        )
    """)

    db.commit()
# ============================================================
# CODEMASTER CONTEST SYSTEM
# LIVE / UPCOMING / FINISHED
# ============================================================


CONTEST_DB = DATABASE


# ============================================================
# DATABASE CONNECTION
# ============================================================

def contest_db():
    conn = sqlite3.connect(CONTEST_DB)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# CURRENT SERVER TIME
# ============================================================

def contest_now():
    return datetime.now()


# ============================================================
# CONTEST STATUS
# ============================================================

# ============================================================
# CONTEST API - COMMON HELPER
# ============================================================

def get_contest_status(start_time, end_time):

    try:
        start = datetime.strptime(
            str(start_time),
            "%Y-%m-%d %H:%M:%S"
        )

        end = datetime.strptime(
            str(end_time),
            "%Y-%m-%d %H:%M:%S"
        )

        now = datetime.now()

        if now < start:
            return "upcoming"

        elif now < end:
            return "live"

        else:
            return "finished"

    except Exception as e:

        print("Contest status error:", e)

        return "upcoming"


# ============================================================
# CREATE CONTEST TABLE
# ============================================================



# ============================================================
# INITIALIZE CONTEST SYSTEM
# ============================================================



def ensure_user_solved_problems_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_solved_problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_id INTEGER NOT NULL,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, problem_id)
            )
        """)

        conn.commit()

        print("User solved problems table: READY")

    except Exception as e:
        conn.rollback()
        print("USER SOLVED PROBLEMS ERROR:", e)
        raise

    finally:
        conn.close()
def ensure_user_problem_codes_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_problem_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                code TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, problem_id, language)
            )
        """)

        conn.commit()

        print("User problem codes table: READY")

    except Exception as e:
        conn.rollback()
        print("USER PROBLEM CODES ERROR:", e)
        raise

    finally:
        conn.close()
    # Tables are created by the dedicated initialization functions above.


# ==========================================
# Home
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================
# CALCULATE REAL USER RATING
# ============================================================
def seed_contests():

    ensure_contest_table()


    conn = get_db_connection()

    try:

        count =conn.execute(
                "SELECT COUNT(*) AS total FROM contests"
            ).fetchone()["total"]


        if count > 0:
            return


        now = datetime.now()


        # =========================================
        # LIVE CONTEST
        # =========================================

        live_start =now - timedelta(minutes=30)


        live_end =now + timedelta(hours=1, minutes=30)


        # =========================================
        # UPCOMING CONTEST
        # =========================================

        upcoming_start =now + timedelta(hours=2)


        upcoming_end =upcoming_start + timedelta(hours=3)


        # =========================================
        # FINISHED CONTEST
        # =========================================

        finished_start =now - timedelta(days=1, hours=3)


        finished_end =now - timedelta(days=1)


        contests = [

            (
                "Weekly Coding Challenge",
                "Weekly Coding Challenge",
                "Solve challenging programming problems and compete with developers on the CodeMaster platform.",
                120,
                live_start.strftime("%Y-%m-%d %H:%M:%S"),
                live_end.strftime("%Y-%m-%d %H:%M:%S"),
                "live",
                1250
            ),

            (
                "Monthly Challenge",
                "Monthly Challenge",
                "Take part in the monthly coding challenge and climb the CodeMaster leaderboard.",
                180,
                upcoming_start.strftime("%Y-%m-%d %H:%M:%S"),
                upcoming_end.strftime("%Y-%m-%d %H:%M:%S"),
                "upcoming",
                850
            ),

            (
                "Algorithm Contest",
                "Algorithm Contest",
                "Test your algorithmic thinking with a collection of challenging programming problems.",
                180,
                finished_start.strftime("%Y-%m-%d %H:%M:%S"),
                finished_end.strftime("%Y-%m-%d %H:%M:%S"),
                "finished",
                1600
            )

        ]


        conn.executemany("""
            INSERT INTO contests
            (
                title,
                name,
                description,
                duration,
                start_time,
                end_time,
                status,
                participants
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, contests)


        conn.commit()


        print(
            "Contest data inserted successfully."
        )


    finally:

        conn.close()

@app.route(
    "/api/contests/<int:contest_id>/register",
    methods=["POST"]
)
def register_for_contest(
    contest_id
):

    ensure_contest_registration_table()


    user_id = (
        session.get("user_id")
        or session.get("id")
    )


    if not user_id:

        return jsonify({
            "success": False,
            "message":
                "Please login before registering."
        }), 401


    refresh_contest_status()


    conn = get_db_connection()

    try:

        contest = conn.execute("""
            SELECT
                id,
                status
            FROM contests
            WHERE id = ?
        """, (
            contest_id,
        )).fetchone()


        if not contest:

            return jsonify({
                "success": False,
                "message":
                    "Contest not found."
            }), 404


        if contest["status"] == "finished":

            return jsonify({
                "success": False,
                "message":
                    "This contest has already finished."
            }), 400


        existing = conn.execute("""
            SELECT id
            FROM contest_registrations
            WHERE contest_id = ?
            AND user_id = ?
        """, (
            contest_id,
            user_id
        )).fetchone()


        if existing:

            return jsonify({
                "success": True,
                "message":
                    "You are already registered."
            })


        conn.execute("""
            INSERT INTO contest_registrations
            (
                contest_id,
                user_id,
                registered_at
            )
            VALUES (?, ?, ?)
        """, (
            contest_id,
            user_id,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ))


        conn.execute("""
            UPDATE contests
            SET participants =
                COALESCE(participants, 0) + 1
            WHERE id = ?
        """, (
            contest_id,
        ))


        conn.commit()


        return jsonify({
            "success": True,
            "message":
                "Successfully registered for the contest!"
        })


    except sqlite3.IntegrityError:

        return jsonify({
            "success": True,
            "message":
                "You are already registered."
        })


    finally:

        conn.close()


@app.route("/contest/<int:contest_id>")
def enter_contest(
    contest_id
):

    refresh_contest_status()


    conn = get_db_connection()

    try:

        contest = conn.execute("""
            SELECT
                id,
                COALESCE(
                    NULLIF(title, ''),
                    name,
                    'Coding Contest'
                ) AS title,
                description,
                duration,
                start_time,
                end_time,
                status
            FROM contests
            WHERE id = ?
        """, (
            contest_id,
        )).fetchone()


        if not contest:

            return (
                "Contest not found",
                404
            )


        return render_template(
            "contest_detail.html",
            contest=dict(contest)
        )


    finally:

        conn.close()
def refresh_contest_status():

    ensure_contest_table()

    conn = get_db_connection()

    try:

        now = datetime.now()

        rows = conn.execute("""
            SELECT
                id,
                start_time,
                end_time
            FROM contests
        """).fetchall()


        for row in rows:

            contest_id = row["id"]

            start_value = row["start_time"]

            end_value = row["end_time"]


            if not start_value or not end_value:
                continue


            try:

                start_time = datetime.strptime(
                    start_value,
                    "%Y-%m-%d %H:%M:%S"
                )


                end_time = datetime.strptime(
                    end_value,
                    "%Y-%m-%d %H:%M:%S"
                )

            except ValueError:

                try:

                    start_time = datetime.fromisoformat(
                        start_value
                    )


                    end_time = datetime.fromisoformat(
                        end_value
                    )

                except Exception:

                    continue


            if now < start_time:

                status = "upcoming"

            elif start_time <= now <= end_time:

                status = "live"

            else:

                status = "finished"


            conn.execute("""
                UPDATE contests
                SET status = ?
                WHERE id = ?
            """, (
                status,
                contest_id
            ))


        conn.commit()


    finally:

        conn.close()

# ==========================================
# Contests
# ==========================================

@app.route("/contests")
def contests():

    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.*,

            (
                SELECT COUNT(*)
                FROM contest_registrations r
                WHERE r.contest_id = c.id
            ) AS registered_count,

            (
                SELECT COUNT(DISTINCT a.user_id)
                FROM contest_attempts a
                WHERE a.contest_id = c.id
            ) AS attempt_count,

            (
                SELECT COUNT(DISTINCT s.problem_id)
                FROM contest_solves s
                WHERE s.contest_id = c.id
            ) AS solved_problem_count

        FROM contests c
        ORDER BY c.start_time ASC
    """)

    rows = cursor.fetchall()

    contests_data = [
        dict(row)
        for row in rows
    ]

    conn.close()

    return render_template(
        "contest.html",
        contests=contests_data
    )
@app.route("/api/contests", methods=["GET"])
def api_contests():

    refresh_contest_status()


    conn = get_db_connection()

    try:

        rows = conn.execute("""
            SELECT
                id,
                COALESCE(
                    NULLIF(title, ''),
                    name,
                    'Coding Contest'
                ) AS title,
                description,
                duration,
                start_time,
                end_time,
                status,
                COALESCE(participants, 0)
                    AS participants
            FROM contests
            ORDER BY
                CASE status
                    WHEN 'live' THEN 1
                    WHEN 'upcoming' THEN 2
                    WHEN 'finished' THEN 3
                    ELSE 4
                END,
                start_time ASC
        """).fetchall()


        contests = []


        for row in rows:

            contest = dict(row)


            # ---------------------------------
            # Problem count
            # ---------------------------------

            contest["problem_count"] = 5


            # ---------------------------------
            # Registered state
            # ---------------------------------

            contest["registered"] = False


            user_id = (
                session.get("user_id")
                or session.get("id")
            )


            if user_id:

                try:

                    registered_table = conn.execute("""
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'table'
                        AND name = 'contest_registrations'
                    """).fetchone()


                    if registered_table:

                        registered =conn.execute("""
                                SELECT 1
                                FROM contest_registrations
                                WHERE contest_id = ?
                                AND user_id = ?
                                LIMIT 1
                            """, (
                                row["id"],
                                user_id
                            )).fetchone()


                        contest["registered"] =registered is not None

                except Exception:

                    contest["registered"] = False


            contests.append(
                contest
            )


        return jsonify(
            contests
        )


    finally:

        conn.close() 

def ensure_contest_registration_table():

    conn = get_db_connection()

    try:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS contest_registrations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                contest_id INTEGER NOT NULL,

                user_id INTEGER NOT NULL,

                registered_at TEXT NOT NULL,

                UNIQUE(contest_id, user_id)

            )
        """)

        conn.commit()

    finally:

        conn.close() 
def get_user_rating(user_id):
    conn = get_db_connection()

    try:
        row = conn.execute("""
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN LOWER(TRIM(p.difficulty)) = 'easy'
                                THEN 10

                            WHEN LOWER(TRIM(p.difficulty)) = 'medium'
                                THEN 20

                            WHEN LOWER(TRIM(p.difficulty)) = 'hard'
                                THEN 30

                            ELSE 0
                        END
                    ),
                    0
                ) AS rating
            FROM user_solved_problems usp

            INNER JOIN problems p
                ON p.id = usp.problem_id

            WHERE usp.user_id = ?
        """, (user_id,)).fetchone()

        return int(row["rating"] or 0)

    finally:
        conn.close()

# ============================================================
# CALCULATE REAL SOLVED PROBLEMS
# ============================================================

def get_user_solved_count(user_id):
    conn = get_db_connection()

    try:
        row = conn.execute("""
            SELECT COUNT(DISTINCT problem_id) AS solved
            FROM user_solved_problems
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        return int(row["solved"] or 0)

    finally:
        conn.close()
# ==========================================
# Register
# ==========================================

# ==========================================
# Google Login
# ==========================================



# ============================================================
# GET REAL-TIME CONTESTS
# ============================================================


# ============================================================
# LIVE CONTESTS API
# ============================================================






@app.route("/google/login")
def google_login():

    redirect_uri = url_for(
        "google_callback",
        _external=True
    )

    return google.authorize_redirect(redirect_uri)




@app.route("/google/callback")
def google_callback():

    try:
        # Google nundi access token
        token = google.authorize_access_token()

        # Google user information
        userinfo = token.get("userinfo")

        if not userinfo:
            return "Google user information not found", 400

        # Google details
        email = userinfo.get("email")
        fullname = userinfo.get("name")
        google_id = userinfo.get("sub")

        if not email:
            return "Google email not found", 400

        conn = get_db_connection()

        try:
            # Existing user ni email tho search cheyyi
            user = conn.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            # User already database lo unte
            if user:

                session.clear()

                session["logged_in"] = True
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["fullname"] = user["fullname"]
                session["email"] = user["email"]
                session["user_email"] = user["email"]
            else:
                # New Google user kosam username
                username = email.split("@")[0]

                # Same username already unda check
                existing_username = conn.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE username = ?
                    """,
                    (username,)
                ).fetchone()

                # Username already unte unique username create
                if existing_username:
                    username = username + "_google"

                # New user create
                conn.execute(
                    """
                    INSERT INTO users
                    (fullname, email, username, password)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        fullname,
                        email,
                        username,
                        "GOOGLE_LOGIN"
                    )
                )

                conn.commit()

                # Normal login route EXACT SAME session
                # Get newly created user
            new_user = conn.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            # Same session structure as normal login
            session.clear()

            session["logged_in"] = True
            session["user_id"] = new_user["id"]
            session["username"] = new_user["username"]
            session["fullname"] = new_user["fullname"]
            session["email"] = new_user["email"]
            session["user_email"] = new_user["email"]

        finally:
            conn.close()

        # Direct dashboard
        return redirect(url_for("dashboard"))

    except Exception as e:

        print("Google Login Error:", e)

        return f"Google Login Failed: {e}", 500



@app.route("/login", methods=["GET", "POST"])
def login():

    # ==========================================
    # GET REQUEST
    # ==========================================

    if request.method == "GET":

        return render_template("login.html")


    # ==========================================
    # POST REQUEST
    # ==========================================

    email = request.form.get(
        "email",
        ""
    ).strip()


    password = request.form.get(
        "password",
        ""
    )


    remember = request.form.get(
        "remember"
    )


    # ==========================================
    # BASIC VALIDATION
    # ==========================================

    if not email:

        flash(
            "Please enter your email.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    if not password:

        flash(
            "Please enter your password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    conn = get_db_connection()


    try:

        # ==========================================
        # FIND USER
        # ==========================================

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            LIMIT 1
            """,
            (email,)
        ).fetchone()


        # ==========================================
        # USER NOT FOUND
        # ==========================================

        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # ==========================================
        # PASSWORD CHECK
        # ==========================================

        stored_password = user["password"]

        password_ok = False


        # =====================================================
        # NEW USERS - HASHED PASSWORD
        # =====================================================

        try:

            password_ok = check_password_hash(
                stored_password,
                password
            )

        except Exception:

            password_ok = False


        # =====================================================
        # OLD USERS - PLAIN TEXT PASSWORD
        # =====================================================

        if not password_ok:

            if stored_password == password:

                password_ok = True

                # =================================================
                # CONVERT OLD PASSWORD TO HASH
                # =================================================

                new_hashed_password = generate_password_hash(
                    password
                )


                conn.execute(
                    """
                    UPDATE users
                    SET password = ?
                    WHERE id = ?
                    """,
                    (
                        new_hashed_password,
                        user["id"]
                    )
                )


                conn.commit()


        # ==========================================
        # WRONG PASSWORD
        # ==========================================

        if not password_ok:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # ==========================================
        # LOGIN SUCCESS
        # ==========================================

        session.clear()


        # ==========================================
        # CREATE SESSION
        # ==========================================

        session["logged_in"] = True

        session["user_id"] = user["id"]

        session["username"] = user["username"]

        session["email"] = user["email"]

        session["user_email"] = user["email"]


        # ==========================================
        # REMEMBER ME
        # ==========================================

        if remember:

            session.permanent = True

        else:

            session.permanent = False


        # ==========================================
        # LOGIN SUCCESS
        # ==========================================

        return redirect(
            url_for("dashboard")
        )


    except sqlite3.Error as e:

        print(
            "LOGIN DATABASE ERROR:",
            e
        )


        flash(
            "Unable to connect to database. Please try again.",
            "error"
        )


        return redirect(
            url_for("login")
        )


    finally:

        conn.close()


# ==========================================
# Login
# ==========================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        language = request.form.get("language", "").strip()

        profile_image = request.files.get("profile_image")


        # =====================================================
        # BASIC VALIDATION
        # =====================================================

        if not fullname or not email or not username or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(url_for("register"))


        # =====================================================
        # CONFIRM PASSWORD
        # =====================================================

        if password != confirm_password:

            flash(
                "Password and Confirm Password do not match.",
                "error"
            )

            return redirect(url_for("register"))


        conn = get_db_connection()


        try:

            # =====================================================
            # CHECK USERNAME / EMAIL
            # =====================================================

            existing_user = conn.execute(
                """
                SELECT id
                FROM users
                WHERE username = ? OR email = ?
                """,
                (username, email)
            ).fetchone()


            if existing_user:

                flash(
                    "Username or email already exists.",
                    "error"
                )

                return redirect(url_for("register"))


            # =====================================================
            # SAVE PROFILE IMAGE
            # =====================================================

            image_filename = None


            if profile_image and profile_image.filename:

                upload_folder = os.path.join(
                    app.root_path,
                    "static",
                    "profile_images"
                )


                os.makedirs(
                    upload_folder,
                    exist_ok=True
                )


                extension = os.path.splitext(
                    profile_image.filename
                )[1].lower()


                # Allow only image extensions

                allowed_extensions = {
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                }


                if extension not in allowed_extensions:

                    flash(
                        "Only JPG, JPEG, PNG and WEBP images are allowed.",
                        "error"
                    )

                    return redirect(url_for("register"))


                image_filename = (
                    str(uuid.uuid4()) + extension
                )


                profile_image.save(
                    os.path.join(
                        upload_folder,
                        image_filename
                    )
                )


            # =====================================================
            # HASH PASSWORD
            # =====================================================

            hashed_password = generate_password_hash(
                password
            )


            # =====================================================
            # INSERT USER
            # =====================================================

            conn.execute(
                """
                INSERT INTO users
                (
                    fullname,
                    email,
                    username,
                    phone,
                    password,
                    language,
                    profile_image
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fullname,
                    email,
                    username,
                    phone,
                    hashed_password,
                    language,
                    image_filename
                )
            )


            conn.commit()


            # =====================================================
            # SUCCESS
            # =====================================================

            flash(
                "Registration successful! Please login.",
                "success"
            )


            return redirect(
                url_for("login")
            )


        except sqlite3.Error as e:

            conn.rollback()

            print(
                "REGISTER DATABASE ERROR:",
                e
            )


            flash(
                "Registration failed. Please try again.",
                "error"
            )


            return redirect(
                url_for("register")
            )


        finally:

            conn.close()


    return render_template("register.html")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        # User entered email
        email = request.form.get('email')

        # Check email entered or not
        if not email:
            flash('Please enter your email')
            return redirect('/forgot-password')

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP and expiry in session
        session['reset_email'] = email
        session['reset_otp'] = otp
        session['reset_otp_expiry'] = (
            datetime.now() + timedelta(seconds=60)
        ).strftime('%Y-%m-%d %H:%M:%S')

        print('Generated OTP:', otp)

        try:
            # Send OTP email
            msg = Message(
                subject='Password Reset OTP',
                recipients=[email]
            )

            msg.body = f'''
Your OTP is: {otp}

This OTP is valid for 60 seconds.
Do not share this OTP with anyone.
'''

            mail.send(msg)

            flash('OTP sent successfully to your email')
            return redirect('/verify-otp')

        except Exception as e:
            print('Mail Error:', e)
            flash('Failed to send OTP. Please try again.')
            return redirect('/forgot-password')

    return render_template('forgot_password.html')

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    try:
        email = session.get('reset_email')

        if not email:
            return jsonify({'message': 'Email session expired'}), 400

        otp = str(random.randint(100000, 999999))

        session['reset_otp'] = otp
        session['reset_otp_expiry'] = (
    datetime.now() + timedelta(seconds=60)
).strftime('%Y-%m-%d %H:%M:%S')
        msg = Message(
            subject='Your New OTP - CodeMaster',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f'Your new OTP is: {otp}'

        mail.send(msg)

        print('New OTP sent:', otp)

        return jsonify({'message': 'New OTP sent successfully'})

    except Exception as e:
        print('Resend OTP Error:', e)
        return jsonify({'message': str(e)}), 500
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    # No email session
    if "reset_email" not in session:

        flash(
            "Please request OTP again.",
            "error"
        )

        return redirect(url_for("forgot_password"))

    # No OTP session
    if "reset_otp" not in session:

        flash(
            "OTP expired. Please request a new OTP.",
            "error"
        )

        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        entered_otp = request.form.get("otp", "").strip()

        saved_otp = session.get("reset_otp")

        created_time = session.get("reset_otp_created")

        # Empty OTP
        if not entered_otp:

            flash(
                "Please enter the OTP.",
                "error"
            )

            return redirect(url_for("verify_otp"))

        # Check expiry
        if created_time:

            try:

                created = datetime.fromisoformat(created_time)

                if datetime.now() - created > timedelta(minutes=10):

                    session.pop("reset_otp", None)
                    session.pop("reset_otp_created", None)

                    flash(
                        "OTP expired. Please request a new OTP.",
                        "error"
                    )

                    return redirect(url_for("forgot_password"))

            except ValueError:
                pass

        # Verify OTP
        if entered_otp == saved_otp:

            session["otp_verified"] = True

            session.pop("reset_otp", None)
            session.pop("reset_otp_created", None)

            return redirect(url_for("reset_password"))

        else:

            flash(
                "Invalid OTP. Please check your email and try again.",
                "error"
            )

            return redirect(url_for("verify_otp"))

    return render_template("verify_otp.html")
def ensure_contest_table():

    conn = get_db_connection()

    try:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS contests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                name TEXT,
                description TEXT,
                duration INTEGER DEFAULT 120,
                start_time TEXT,
                end_time TEXT,
                status TEXT DEFAULT 'upcoming',
                participants INTEGER DEFAULT 0
            )
        """)

        conn.commit()


        # Get existing columns

        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(contests)"
            ).fetchall()
        ]


        # Add missing columns safely

        required_columns = {

            "title":
                "ALTER TABLE contests ADD COLUMN title TEXT",

            "name":
                "ALTER TABLE contests ADD COLUMN name TEXT",

            "description":
                "ALTER TABLE contests ADD COLUMN description TEXT",

            "duration":
                "ALTER TABLE contests ADD COLUMN duration INTEGER DEFAULT 120",

            "start_time":
                "ALTER TABLE contests ADD COLUMN start_time TEXT",

            "end_time":
                "ALTER TABLE contests ADD COLUMN end_time TEXT",

            "status":
                "ALTER TABLE contests ADD COLUMN status TEXT DEFAULT 'upcoming'",

            "participants":
                "ALTER TABLE contests ADD COLUMN participants INTEGER DEFAULT 0"

        }


        for column, sql in required_columns.items():

            if column not in columns:

                conn.execute(sql)


        conn.commit()


    finally:

        conn.close()

        
# ============================================================
# DOWNLOAD LANGUAGE CERTIFICATE
# ============================================================
@app.route("/api/run-code", methods=["POST"])
def api_run_code():
    import os
    import sys
    import tempfile
    import subprocess

    try:
        data = request.get_json(silent=True) or {}

        code = data.get("code", "")
        language = str(data.get("language", "python")).lower()
        user_input = data.get("input", "")

        if not code.strip():
            return jsonify({
                "success": False,
                "error": "Code is empty."
            }), 400

        with tempfile.TemporaryDirectory() as temp_dir:

            if language == "python":
                filename = os.path.join(
                    temp_dir,
                    "main.py"
                )

                with open(
                    filename,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                result = subprocess.run(
                    [
                        sys.executable,
                        filename
                    ],
                    input=user_input,
                    text=True,
                    capture_output=True,
                    timeout=10
                )

            elif language == "java":
                filename = os.path.join(
                    temp_dir,
                    "Main.java"
                )

                with open(
                    filename,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                compile_result = subprocess.run(
                    [
                        "javac",
                        filename
                    ],
                    text=True,
                    capture_output=True,
                    timeout=10
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": False,
                        "error": compile_result.stderr
                    }), 400

                result = subprocess.run(
                    [
                        "java",
                        "-cp",
                        temp_dir,
                        "Main"
                    ],
                    input=user_input,
                    text=True,
                    capture_output=True,
                    timeout=10
                )

            elif language in ("c", "cpp", "c++"):

                extension = (
                    "cpp"
                    if language in ("cpp", "c++")
                    else "c"
                )

                filename = os.path.join(
                    temp_dir,
                    "main." + extension
                )

                executable = os.path.join(
                    temp_dir,
                    "main.exe"
                )

                with open(
                    filename,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                compiler = (
                    "g++"
                    if extension == "cpp"
                    else "gcc"
                )

                compile_result = subprocess.run(
                    [
                        compiler,
                        filename,
                        "-o",
                        executable
                    ],
                    text=True,
                    capture_output=True,
                    timeout=10
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": False,
                        "error": compile_result.stderr
                    }), 400

                result = subprocess.run(
                    [executable],
                    input=user_input,
                    text=True,
                    capture_output=True,
                    timeout=10
                )

            else:
                return jsonify({
                    "success": False,
                    "error": "Unsupported language."
                }), 400

            if result.returncode != 0:
                return jsonify({
                    "success": False,
                    "error": result.stderr or "Runtime Error"
                }), 400

            return jsonify({
                "success": True,
                "output": result.stdout.strip()
            })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Time Limit Exceeded"
        }), 408

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route(
    "/download-language-certificate/<language>"
)
def download_language_certificate(language):

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    # --------------------------------------------------------
    # NORMALIZE LANGUAGE
    # --------------------------------------------------------

    language = normalize_language(language)

    allowed_languages = [
        "python",
        "java",
        "cpp",
        "c"
    ]

    if language not in allowed_languages:
        return "Invalid programming language.", 400

    conn = get_db()

    try:

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        user = conn.execute("""
            SELECT
                id,
                fullname,
                username,
                email
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        if not user:
            return redirect(url_for("login"))

        # ----------------------------------------------------
        # CHECK 135 PROBLEMS
        # ----------------------------------------------------

        row = conn.execute("""
            SELECT COUNT(DISTINCT problem_id) AS total
            FROM user_problem_progress
            WHERE user_id = ?
            AND LOWER(language) = ?
        """, (
            user_id,
            language
        )).fetchone()

        solved_count = row["total"] if row else 0

        if solved_count < 135:

            return (
                f"Certificate locked. "
                f"Complete 135 {language.upper()} problems first.",
                403
            )

        # ----------------------------------------------------
        # GET / CREATE CERTIFICATE
        # ----------------------------------------------------

        certificate = conn.execute("""
            SELECT
                certificate_id,
                issued_at
            FROM language_certificates
            WHERE user_id = ?
            AND language = ?
        """, (
            user_id,
            language
        )).fetchone()

        if not certificate:

            year = datetime.now().year

            random_code = uuid.uuid4().hex[:8].upper()

            certificate_id = (
                f"CM-{year}-"
                f"{int(user_id):06d}-"
                f"{random_code}"
            )

            conn.execute("""
                INSERT INTO language_certificates
                (
                    user_id,
                    language,
                    certificate_id
                )
                VALUES (?, ?, ?)
            """, (
                user_id,
                language,
                certificate_id
            ))

            conn.commit()

            certificate = conn.execute("""
                SELECT
                    certificate_id,
                    issued_at
                FROM language_certificates
                WHERE user_id = ?
                AND language = ?
            """, (
                user_id,
                language
            )).fetchone()

        # ----------------------------------------------------
        # CREATE PDF
        # ----------------------------------------------------

        buffer = io.BytesIO()

        page_width, page_height = landscape(A4)

        pdf = canvas.Canvas(
            buffer,
            pagesize=(page_width, page_height)
        )

        # ====================================================
        # COLORS
        # ====================================================

        navy = colors.HexColor("#061426")
        navy2 = colors.HexColor("#0A1E38")

        gold = colors.HexColor("#F5C542")
        gold2 = colors.HexColor("#FFD966")

        cyan = colors.HexColor("#20BFFF")

        white = colors.HexColor("#FFFFFF")

        muted = colors.HexColor("#A8B7CC")

        dark_gold = colors.HexColor("#9A7512")

        # ====================================================
        # BACKGROUND
        # ====================================================

        pdf.setFillColor(navy)

        pdf.rect(
            0,
            0,
            page_width,
            page_height,
            fill=1,
            stroke=0
        )

        # ====================================================
        # OUTER GOLD BORDER
        # ====================================================

        pdf.setStrokeColor(gold)

        pdf.setLineWidth(7)

        pdf.roundRect(
            18,
            18,
            page_width - 36,
            page_height - 36,
            16,
            fill=0,
            stroke=1
        )

        # ====================================================
        # INNER BORDER
        # ====================================================

        pdf.setStrokeColor(
            colors.HexColor("#174A75")
        )

        pdf.setLineWidth(1.2)

        pdf.roundRect(
            38,
            38,
            page_width - 76,
            page_height - 76,
            10,
            fill=0,
            stroke=1
        )

        # ====================================================
        # TOP LEFT CODEMASTER
        # ====================================================

        pdf.setFont(
            "Helvetica-Bold",
            24
        )

        pdf.setFillColor(cyan)

        pdf.drawString(
            60,
            page_height - 75,
            "</>"
        )

        pdf.setFillColor(white)

        pdf.drawString(
            110,
            page_height - 75,
            "Code"
        )

        pdf.setFillColor(cyan)

        pdf.drawString(
            170,
            page_height - 75,
            "Master"
        )

        pdf.setFont(
            "Helvetica",
            8
        )

        pdf.setFillColor(muted)

        pdf.drawString(
            112,
            page_height - 91,
            "LEARN  •  PRACTICE  •  ACHIEVE"
        )

        # ====================================================
        # TOP RIGHT CERTIFICATE ID
        # ====================================================

        pdf.setFont(
            "Helvetica",
            7
        )

        pdf.setFillColor(muted)

        pdf.drawRightString(
            page_width - 62,
            page_height - 63,
            "CERTIFICATE ID"
        )

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.setFillColor(gold)

        pdf.drawRightString(
            page_width - 62,
            page_height - 80,
            certificate["certificate_id"]
        )

        # ====================================================
        # MEDALLION
        # ====================================================

        center_x = page_width / 2

        medal_y = page_height - 85

        pdf.setFillColor(
            colors.HexColor("#0D2945")
        )

        pdf.setStrokeColor(gold)

        pdf.setLineWidth(3)

        pdf.circle(
            center_x,
            medal_y,
            40,
            fill=1,
            stroke=1
        )

        pdf.setFillColor(gold)

        pdf.setFont(
            "Helvetica-Bold",
            27
        )

        pdf.drawCentredString(
            center_x,
            medal_y - 10,
            "★"
        )

        # ====================================================
        # TITLE
        # ====================================================

        pdf.setFont(
            "Helvetica",
            20
        )

        pdf.setFillColor(white)

        pdf.drawCentredString(
            center_x,
            page_height - 145,
            "C E R T I F I C A T E   O F"
        )

        pdf.setFont(
            "Helvetica-Bold",
            38
        )

        pdf.setFillColor(gold2)

        pdf.drawCentredString(
            center_x,
            page_height - 190,
            "CODING EXCELLENCE"
        )

        # ====================================================
        # SUBTITLE
        # ====================================================

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.setFillColor(muted)

        pdf.drawCentredString(
            center_x,
            page_height - 213,
            "ACHIEVEMENT  •  RECOGNITION  •  EXCELLENCE"
        )

        # ====================================================
        # PRESENTED TO
        # ====================================================

        pdf.setFont(
            "Helvetica",
            9
        )

        pdf.setFillColor(muted)

        pdf.drawCentredString(
            center_x,
            page_height - 258,
            "THIS CERTIFICATE IS PROUDLY PRESENTED TO"
        )

        # ====================================================
        # USER NAME
        # ====================================================

        fullname = user["fullname"] or user["username"]

        pdf.setFont(
            "Helvetica-BoldOblique",
            32
        )

        pdf.setFillColor(gold2)

        pdf.drawCentredString(
            center_x,
            page_height - 300,
            fullname.title()
        )

        # ====================================================
        # NAME LINE
        # ====================================================

        pdf.setStrokeColor(gold)

        pdf.setLineWidth(1)

        pdf.line(
            center_x - 190,
            page_height - 315,
            center_x + 190,
            page_height - 315
        )

        # ====================================================
        # LANGUAGE
        # ====================================================

        language_names = {
            "python": "PYTHON PROGRAMMING",
            "java": "JAVA PROGRAMMING",
            "cpp": "C++ PROGRAMMING",
            "c": "C PROGRAMMING"
        }

        language_title = language_names[language]

        pdf.setFont(
            "Helvetica-Bold",
            18
        )

        pdf.setFillColor(cyan)

        pdf.drawCentredString(
            center_x,
            page_height - 350,
            language_title
        )

        # ====================================================
        # DESCRIPTION
        # ====================================================

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.setFillColor(white)

        pdf.drawCentredString(
            center_x,
            page_height - 385,
            "In recognition of successfully demonstrating"
        )

        pdf.drawCentredString(
            center_x,
            page_height - 401,
            "programming and problem-solving skills in"
        )

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.setFillColor(cyan)

        pdf.drawCentredString(
            center_x,
            page_height - 417,
            language_title
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.setFillColor(white)

        pdf.drawCentredString(
            center_x,
            page_height - 433,
            "by successfully completing 10 unique coding problems."
        )

        # ====================================================
        # STATS
        # ====================================================

        stat_y = page_height - 485

        stat_positions = [
            center_x - 150,
            center_x,
            center_x + 150
        ]

        stat_values = [
            "10",
            language.upper(),
            "100%"
        ]

        stat_labels = [
            "PROBLEMS SOLVED",
            "LANGUAGE",
            "ACHIEVEMENT"
        ]

        for i in range(3):

            x = stat_positions[i]

            pdf.setFont(
                "Helvetica-Bold",
                21 if i != 1 else 14
            )

            pdf.setFillColor(gold2)

            pdf.drawCentredString(
                x,
                stat_y,
                stat_values[i]
            )

            pdf.setFont(
                "Helvetica",
                7
            )

            pdf.setFillColor(muted)

            pdf.drawCentredString(
                x,
                stat_y - 16,
                stat_labels[i]
            )

        # ====================================================
        # VERTICAL DIVIDERS
        # ====================================================

        pdf.setStrokeColor(
            colors.HexColor("#52647A")
        )

        pdf.setLineWidth(0.7)

        pdf.line(
            center_x - 75,
            stat_y - 22,
            center_x - 75,
            stat_y + 22
        )

        pdf.line(
            center_x + 75,
            stat_y - 22,
            center_x + 75,
            stat_y + 22
        )

        # ====================================================
        # SIGNATURE
        # ====================================================

        pdf.setStrokeColor(
            colors.HexColor("#72849A")
        )

        pdf.line(
            70,
            82,
            230,
            82
        )

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.setFillColor(white)

        pdf.drawCentredString(
            150,
            65,
            "CodeMaster"
        )

        pdf.setFont(
            "Helvetica",
            7
        )

        pdf.setFillColor(muted)

        pdf.drawCentredString(
            150,
            53,
            "Authorized Certification"
        )

        # ====================================================
        # ISSUE DATE
        # ====================================================

        issued_at = certificate["issued_at"]

        if issued_at:

            try:
                date_obj = datetime.strptime(
                    str(issued_at),
                    "%Y-%m-%d %H:%M:%S"
                )

                issue_date = date_obj.strftime(
                    "%d %B %Y"
                )

            except Exception:

                issue_date = str(issued_at)

        else:

            issue_date = datetime.now().strftime(
                "%d %B %Y"
            )

        pdf.setFont(
            "Helvetica",
            7
        )

        pdf.setFillColor(muted)

        pdf.drawCentredString(
            page_width - 150,
            82,
            "ISSUED DATE"
        )

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.setFillColor(gold2)

        pdf.drawCentredString(
            page_width - 150,
            64,
            issue_date
        )

        # ====================================================
        # FOOTER
        # ====================================================

        pdf.setFont(
            "Helvetica",
            7
        )

        pdf.setFillColor(
            colors.HexColor("#5F7691")
        )

        pdf.drawCentredString(
            center_x,
            42,
            "CodeMaster  •  Learn  •  Practice  •  Achieve"
        )

        # ====================================================
        # GOLD CORNER DECORATION
        # ====================================================

        pdf.setStrokeColor(gold)

        pdf.setLineWidth(2)

        # bottom-left

        pdf.line(42, 65, 42, 42)
        pdf.line(42, 42, 80, 42)

        # bottom-right

        pdf.line(
            page_width - 42,
            65,
            page_width - 42,
            42
        )

        pdf.line(
            page_width - 80,
            42,
            page_width - 42,
            42
        )

        # top-left

        pdf.line(
            42,
            page_height - 65,
            42,
            page_height - 42
        )

        pdf.line(
            42,
            page_height - 42,
            80,
            page_height - 42
        )

        # top-right

        pdf.line(
            page_width - 42,
            page_height - 65,
            page_width - 42,
            page_height - 42
        )

        pdf.line(
            page_width - 80,
            page_height - 42,
            page_width - 42,
            page_height - 42
        )

        # ====================================================
        # FINISH PDF
        # ====================================================

        pdf.showPage()

        pdf.save()

        buffer.seek(0)

        filename = (
            f"CodeMaster_"
            f"{language_names[language].replace(' ', '_')}_"
            f"Certificate.pdf"
        )

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )

    finally:

        conn.close()
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    if request.method == 'POST':

        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('reset_password'))

        # session lo email store chesam ani assume chestunnam
        email = session.get('reset_email')

        if not email:
            flash('Session expired. Try again.', 'danger')
            return redirect(url_for('forgot_password'))

        # password hash cheyyi
        hashed_password = generate_password_hash(password)

        # database update
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (hashed_password, email)
        )

        conn.commit()
        conn.close()

        flash('Password updated successfully', 'success')

        return redirect(url_for('login'))

    return render_template('reset_password.html')




@app.route("/solve/<int:problem_id>")
def solve_legacy_problem(problem_id):

    if "username" not in session:
        return redirect(url_for("login"))

    problems = {

        1: {
            "title": "Two Sum",
            "difficulty": "Easy",
            "category": "Arrays",
            "description": "Given an array of integers and a target, return the indices of two numbers that add up to the target."
        },

        2: {
            "title": "Palindrome Number",
            "difficulty": "Easy",
            "category": "Math",
            "description": "Given an integer x, return true if x is a palindrome, and false otherwise."
        },

        3: {
            "title": "Valid Anagram",
            "difficulty": "Easy",
            "category": "Strings",
            "description": "Given two strings s and t, return true if t is an anagram of s."
        },

        4: {
            "title": "Valid Palindrome",
            "difficulty": "Easy",
            "category": "Strings",
            "description": "A phrase is a palindrome if it reads the same forward and backward after removing non-alphanumeric characters."
        },

        5: {
            "title": "Best Time to Buy and Sell Stock",
            "difficulty": "Easy",
            "category": "Arrays",
            "description": "Given an array of prices, find the maximum profit you can achieve by buying and selling one stock."
        },

        6: {
            "title": "Longest Substring Without Repeating Characters",
            "difficulty": "Medium",
            "category": "Strings",
            "description": "Find the length of the longest substring without repeating characters."
        },

        7: {
            "title": "3Sum",
            "difficulty": "Medium",
            "category": "Arrays",
            "description": "Find all unique triplets in the array which give the sum of zero."
        },

        8: {
            "title": "Merge Intervals",
            "difficulty": "Medium",
            "category": "Arrays",
            "description": "Given an array of intervals, merge all overlapping intervals."
        },

        9: {
            "title": "Linked List Cycle",
            "difficulty": "Medium",
            "category": "Linked List",
            "description": "Determine whether a linked list contains a cycle."
        },

        10: {
            "title": "Binary Tree Level Order Traversal",
            "difficulty": "Medium",
            "category": "Trees",
            "description": "Return the level order traversal of a binary tree."
        },

        11: {
            "title": "Word Ladder",
            "difficulty": "Hard",
            "category": "Graphs",
            "description": "Find the shortest transformation sequence from beginWord to endWord."
        },

        12: {
            "title": "Edit Distance",
            "difficulty": "Hard",
            "category": "Dynamic Programming",
            "description": "Find the minimum number of operations required to convert one string into another."
        },

        13: {
            "title": "Serialize and Deserialize Binary Tree",
            "difficulty": "Hard",
            "category": "Trees",
            "description": "Design an algorithm to serialize and deserialize a binary tree."
        },

        14: {
            "title": "Alien Dictionary",
            "difficulty": "Hard",
            "category": "Graphs",
            "description": "Given words sorted according to an alien language, determine the ordering of its characters."
        },

        15: {
            "title": "Trapping Rain Water",
            "difficulty": "Hard",
            "category": "Arrays",
            "description": "Given an elevation map, calculate how much rain water can be trapped."
        }

    }

    problem = problems.get(problem_id)

    if problem is None:
        return "Problem not found", 404

    return render_template(
        "solve_problem.html",
        problem=problem,
        problem_id=problem_id
    )



      # ==========================================
# Dashboard
# ==========================================
# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    # ------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    conn = get_db_connection()

    try:

        # ------------------------------------------
        # GET CURRENT USER
        # ------------------------------------------
        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if user is None:

            session.clear()

            flash(
                "User not found. Please login again.",
                "error"
            )

            return redirect(url_for("login"))

        # ------------------------------------------
        # CONVERT ROW TO DICT
        # ------------------------------------------

        user_data = dict(user)

        user_id = user_data["id"]

        # ==================================================
        # REAL SOLVED COUNT
        # ==================================================

        solved_row = conn.execute("""
            SELECT COUNT(DISTINCT problem_id) AS solved
            FROM user_solved_problems
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        solved_count = int(
            solved_row["solved"] or 0
        )

        # ==================================================
        # REAL RATING
        # ==================================================

        rating_row = conn.execute("""
            SELECT
                COALESCE(
                    SUM(
                        CASE

                            WHEN LOWER(TRIM(p.difficulty)) = 'easy'
                                THEN 10

                            WHEN LOWER(TRIM(p.difficulty)) = 'medium'
                                THEN 20

                            WHEN LOWER(TRIM(p.difficulty)) = 'hard'
                                THEN 30

                            ELSE 0

                        END
                    ),
                    0
                ) AS rating

            FROM user_solved_problems usp

            INNER JOIN problems p
                ON p.id = usp.problem_id

            WHERE usp.user_id = ?

        """, (user_id,)).fetchone()

        rating = int(
            rating_row["rating"] or 0
        )

        # ==================================================
        # OVERRIDE OLD DATABASE VALUES
        # ==================================================
        #
        # IMPORTANT:
        # If old database contains rating = 1000,
        # dashboard will NOT use it.
        #
        # It uses actual solved problems.
        #

        user_data["solved"] = solved_count
        user_data["rating"] = rating

        # ==================================================
        # OTHER USER DATA
        # ==================================================

        fullname = user_data.get(
            "fullname",
            ""
        )

        email = user_data.get(
            "email",
            ""
        )

        username_value = user_data.get(
            "username",
            username
        )

        certificates = user_data.get(
            "certificates",
            ""
        )

        rank = user_data.get(
            "rank",
            ""
        )

        phone = user_data.get(
            "phone",
            ""
        )

        college = user_data.get(
            "college",
            ""
        )

        branch = user_data.get(
            "branch",
            ""
        )

        skills = user_data.get(
            "skills",
            ""
        )

        bio = user_data.get(
            "bio",
            ""
        )

        # ==================================================
        # DASHBOARD
        # ==================================================

        return render_template(
            "dashboard.html",

            user=user_data,

            fullname=fullname,

            email=email,

            username=username_value,

            certificates=certificates,

            rank=rank,

            phone=phone,

            college=college,

            branch=branch,

            skills=skills,

            bio=bio
        )

    except sqlite3.Error as e:

        print(
            "DASHBOARD DATABASE ERROR:",
            e
        )

        flash(
            "Unable to load dashboard.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    finally:

        conn.close()

# ============================================================
# PROBLEM SOLVED
# ============================================================

@app.route("/problem-solved")
def problem_solved():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return redirect(url_for("dashboard"))


# ==========================================
# Problems
# ==========================================
# ==========================================
# Problem Page
# User-wise Saved Code
# ==========================================

# ==========================================
# Problem Page
# User-wise Saved Code
# ==========================================



@app.route("/problem/<int:problem_id>")
def problem(problem_id):

    if not session.get("logged_in") or not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()

    # -----------------------------------------
    # GET PROBLEM
    # -----------------------------------------

    problem = conn.execute(
        """
        SELECT *
        FROM problems
        WHERE id = ?
        """,
        (problem_id,)
    ).fetchone()

    if not problem:
        conn.close()
        return "Problem not found", 404

    # -----------------------------------------
    # GET SAVED LANGUAGE
    # -----------------------------------------

    saved_language_row = conn.execute(
        """
        SELECT language
        FROM user_problem_codes
        WHERE user_id = ?
        AND problem_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (
            user_id,
            problem_id
        )
    ).fetchone()

    saved_language = (
        saved_language_row["language"]
        if saved_language_row
        else "python"
    )

    # -----------------------------------------
    # GET SAVED CODE
    # ONLY CURRENT USER
    # -----------------------------------------

    saved_code_row = conn.execute(
        """
        SELECT code
        FROM user_problem_codes
        WHERE user_id = ?
        AND problem_id = ?
        AND language = ?
        """,
        (
            user_id,
            problem_id,
            saved_language
        )
    ).fetchone()

    saved_code = (
        saved_code_row["code"]
        if saved_code_row
        else ""
    )

    # -----------------------------------------
    # CHECK SOLVED STATUS
    # IMPORTANT:
    # SAVED CODE != SOLVED
    # -----------------------------------------

    solved_row = conn.execute(
        """
        SELECT 1
        FROM user_solved_problems
        WHERE user_id = ?
        AND problem_id = ?
        LIMIT 1
        """,
        (
            user_id,
            problem_id
        )
    ).fetchone()

    is_solved = solved_row is not None

    conn.close()

    return render_template(
        "solve_problem.html",
        problem=problem,
        saved_code=saved_code,
        saved_language=saved_language,
        is_solved=is_solved
    )


# =========================================================
# CONTEST PROBLEMS
# =========================================================

# ==========================================
# Problems
# ==========================================

# ==========================================
# Problems
# ==========================================

@app.route("/problems")
def problems():

    if not session.get("logged_in") or not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()

    try:

        problems_list = conn.execute("""
            SELECT *
            FROM problems
            ORDER BY id
        """).fetchall()

        solved_rows = conn.execute("""
            SELECT problem_id
            FROM user_solved_problems
            WHERE user_id = ?
        """, (user_id,)).fetchall()

        solved_problems = {
            row["problem_id"]
            for row in solved_rows
        }

        return render_template(
            "problems.html",
            problems=problems_list,
            solved_problems=solved_problems
        )

    except sqlite3.Error as e:

        print("PROBLEMS DATABASE ERROR:", e)

        return "Unable to load problems.", 500

    finally:

        conn.close()
# ==========================================
# Code Editor
# ==========================================

@app.route("/editor")
def editor():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("editor.html")


# ==========================================
# Compiler
# ==========================================

@app.route("/compiler")
def compiler():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("editor.html")


# ==========================================
# Leaderboard
# ==========================================
# ==========================================
# GLOBAL LEADERBOARD
# ==========================================

# ==========================================
# LEADERBOARD
# ==========================================

@app.route("/leaderboard")
def leaderboard():

    if not session.get("logged_in") or not session.get("user_id"):
        return redirect(url_for("login"))

    conn = get_db()

    try:

        users = conn.execute("""
            SELECT
                u.id,
                u.fullname,
                u.username,
                u.email,

                COUNT(DISTINCT usp.problem_id) AS problems_solved,

                COALESCE(
                    SUM(
                        CASE
                            WHEN LOWER(TRIM(p.difficulty)) = 'easy'
                                THEN 10

                            WHEN LOWER(TRIM(p.difficulty)) = 'medium'
                                THEN 20

                            WHEN LOWER(TRIM(p.difficulty)) = 'hard'
                                THEN 30

                            ELSE 0
                        END
                    ),
                    0
                ) AS rating

            FROM users u

            LEFT JOIN user_solved_problems usp
                ON u.id = usp.user_id

            LEFT JOIN problems p
                ON p.id = usp.problem_id

            GROUP BY
                u.id,
                u.fullname,
                u.username,
                u.email

            ORDER BY
                rating DESC,
                problems_solved DESC,
                u.id ASC

        """).fetchall()

        leaderboard_data = []

        for index, user in enumerate(users, start=1):

            solved_count = int(
                user["problems_solved"] or 0
            )

            rating = int(
                user["rating"] or 0
            )

            if solved_count >= 100:

                badge = "Grandmaster"
                badge_icon = "🏆"

            elif solved_count >= 75:

                badge = "Master"
                badge_icon = "👑"

            elif solved_count >= 50:

                badge = "Expert"
                badge_icon = "🥇"

            elif solved_count >= 25:

                badge = "Specialist"
                badge_icon = "🥈"

            elif solved_count >= 10:

                badge = "Candidate Master"
                badge_icon = "🥉"

            elif solved_count >= 5:

                badge = "Pupil"
                badge_icon = "⭐"

            else:

                badge = "Beginner"
                badge_icon = "🌱"

            name = (
                user["fullname"]
                or user["username"]
                or "User"
            )

            leaderboard_data.append({

                "rank": index,

                "id": user["id"],

                "name": name,

                "username": user["username"] or "",

                "email": user["email"] or "",

                "problems_solved": solved_count,

                "rating": rating,

                "badge": badge,

                "badge_icon": badge_icon

            })

        current_user_id = session["user_id"]

        current_user = None

        for user in leaderboard_data:

            if user["id"] == current_user_id:

                current_user = user

                break

        top_three = leaderboard_data[:3]

        return render_template(

            "leaderboard.html",

            leaderboard=leaderboard_data,

            top_three=top_three,

            current_user=current_user

        )

    except sqlite3.Error as e:

        print(
            "LEADERBOARD DATABASE ERROR:",
            e
        )

        return "Unable to load leaderboard.", 500

    finally:

        conn.close()

# ============================================================
# CODEMASTER CONTEST SYSTEM
# CREATE -> UPCOMING -> REGISTER -> LIVE -> PROBLEMS
# -> SUBMIT -> SOLVE -> LEADERBOARD -> FINISHED
# ============================================================




# ============================================================
# DATABASE CONNECTION
# ============================================================

def contest_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# CREATE CONTEST TABLES
# ============================================================

    # --------------------------------------------------------
    # REGISTRATIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contest_registrations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            contest_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            registered_at TEXT DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(contest_id, user_id)
        )
    """)

    # --------------------------------------------------------
    # CONTEST PROBLEMS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contest_problems (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            contest_id INTEGER NOT NULL,

            problem_id INTEGER NOT NULL,

            UNIQUE(contest_id, problem_id)
        )
    """)

    # --------------------------------------------------------
    # ATTEMPTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contest_attempts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            contest_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            problem_id INTEGER NOT NULL,

            language TEXT NOT NULL,

            status TEXT NOT NULL,

            attempted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # SOLVES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contest_solves (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            contest_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            problem_id INTEGER NOT NULL,

            solved_at TEXT DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(contest_id, user_id, problem_id)
        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# CONTEST STATUS
# ============================================================

def calculate_contest_status(start_time, end_time):

    try:

        start = datetime.fromisoformat(
            start_time.replace("Z", "+00:00")
        )

        end = datetime.fromisoformat(
            end_time.replace("Z", "+00:00")
        )

        if start.tzinfo is None:
            start = start.replace(
                tzinfo=timezone.utc
            )

        if end.tzinfo is None:
            end = end.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        if now < start:

            return "upcoming"

        if start <= now < end:

            return "live"

        return "finished"

    except Exception:

        return "upcoming"


# ============================================================
# UPDATE CONTEST STATUS

# ============================================================
# ADMIN / CREATE CONTEST
# ============================================================


# ==========================================
# Profile
# ==========================================

@app.route("/profile")
def profile():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    conn = get_db_connection()

    try:

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        if not user:
            return redirect(url_for("login"))

        solved_row = conn.execute("""
            SELECT COUNT(DISTINCT problem_id) AS solved
            FROM user_solved_problems
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        solved_count = int(
            solved_row["solved"] or 0
        )

        rating_row = conn.execute("""
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN LOWER(TRIM(p.difficulty)) = 'easy'
                            THEN 10

                        WHEN LOWER(TRIM(p.difficulty)) = 'medium'
                            THEN 20

                        WHEN LOWER(TRIM(p.difficulty)) = 'hard'
                            THEN 30

                        ELSE 0
                    END
                ),
                0
            ) AS rating

            FROM user_solved_problems usp

            INNER JOIN problems p
                ON p.id = usp.problem_id

            WHERE usp.user_id = ?

        """, (user_id,)).fetchone()

        rating = int(
            rating_row["rating"] or 0
        )

        rank_row = conn.execute("""
            SELECT COUNT(*) + 1 AS rank
            FROM users u
            WHERE (
                SELECT COALESCE(
                    SUM(
                        CASE
                            WHEN LOWER(TRIM(p2.difficulty)) = 'easy'
                                THEN 10

                            WHEN LOWER(TRIM(p2.difficulty)) = 'medium'
                                THEN 20

                            WHEN LOWER(TRIM(p2.difficulty)) = 'hard'
                                THEN 30

                            ELSE 0
                        END
                    ),
                    0
                )

                FROM user_solved_problems usp2

                INNER JOIN problems p2
                    ON p2.id = usp2.problem_id

                WHERE usp2.user_id = u.id

            ) > ?

        """, (rating,)).fetchone()

        rank = int(
            rank_row["rank"] or 1
        )

        user_data = dict(user)

        user_data["solved"] = solved_count
        user_data["rating"] = rating
        user_data["rank"] = rank

        return render_template(
            "profile.html",
            user=user_data
        )

    except sqlite3.Error as e:

        print(
            "PROFILE DATABASE ERROR:",
            e
        )

        return "Unable to load profile.", 500

    finally:

        conn.close()
# ==========================================
# Certificate
# ==========================================




# ==========================================
# Update Profile
# ==========================================

@app.route(
    "/update-profile",
    methods=["POST"]
)
def update_profile():

    if "user_email" not in session:
        return redirect(url_for("login"))


    email = session["user_email"]


    fullname = request.form.get(
        "fullname",
        ""
    ).strip()


    phone = request.form.get(
        "phone",
        ""
    ).strip()


    language = request.form.get(
        "language",
        ""
    ).strip()


    profile_image = request.files.get(
        "profile_image"
    )


    conn = get_db_connection()


    try:

        # -----------------------------------------
        # CURRENT IMAGE
        # -----------------------------------------

        current_user = conn.execute(
            """
            SELECT profile_image
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()


        image_filename = (
            current_user["profile_image"]
            if current_user
            else None
        )


        # -----------------------------------------
        # NEW IMAGE
        # -----------------------------------------

        if (
            profile_image
            and profile_image.filename
        ):

            upload_folder = os.path.join(
                app.root_path,
                "static",
                "profile_images"
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            extension = os.path.splitext(
                profile_image.filename
            )[1].lower()


            image_filename = (
                str(uuid.uuid4())
                + extension
            )


            profile_image.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )


        # -----------------------------------------
        # UPDATE DATABASE
        # -----------------------------------------

        conn.execute(
            """
            UPDATE users
            SET
                fullname = ?,
                phone = ?,
                language = ?,
                profile_image = ?
            WHERE email = ?
            """,
            (
                fullname,
                phone,
                language,
                image_filename,
                email
            )
        )


        conn.commit()


        # Update session fullname

        session["fullname"] = fullname


        flash(
            "Profile updated successfully!",
            "success"
        )


        return redirect(
            url_for("profile")
        )


    except sqlite3.Error as e:

        conn.rollback()

        print(
            "PROFILE UPDATE ERROR:",
            e
        )


        flash(
            "Unable to update profile.",
            "error"
        )


        return redirect(
            url_for("profile")
        )


    finally:

        conn.close()



# ==========================================
# Certificate
# ==========================================
# ============================================================
# CERTIFICATE PAGE
# ============================================================

@app.route("/certificates")
def certificate():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    conn = get_db()

    try:

        # ----------------------------------------------------
        # GET USER
        # ----------------------------------------------------

        user = conn.execute("""
            SELECT
                id,
                fullname,
                username,
                email
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        if not user:
            return redirect(url_for("login"))

        # ----------------------------------------------------
        # LANGUAGE LIST
        # ----------------------------------------------------

        languages = [
            "python",
            "java",
            "cpp",
            "c"
        ]

        progress = {}

        certificates = {}

        # ----------------------------------------------------
        # GET EACH LANGUAGE PROGRESS
        # ----------------------------------------------------

        for language in languages:

            row = conn.execute("""
                SELECT COUNT(DISTINCT problem_id) AS total
                FROM user_problem_progress
                WHERE user_id = ?
                AND LOWER(language) = ?
            """, (
                user_id,
                language
            )).fetchone()

            count = row["total"] if row else 0

            progress[language] = min(count, 135)  # Cap at 135 problems

            # ------------------------------------------------
            # CERTIFICATE
            # ------------------------------------------------

            cert = conn.execute("""
                SELECT
                    certificate_id,
                    issued_at
                FROM language_certificates
                WHERE user_id = ?
                AND language = ?
            """, (
                user_id,
                language
            )).fetchone()

            # ------------------------------------------------
            # CREATE CERTIFICATE AFTER 135 PROBLEMS
            # ------------------------------------------------

            if count >= 135 and not cert:

                year = datetime.now().year

                random_code = uuid.uuid4().hex[:8].upper()

                certificate_id = (
                    f"CM-{year}-"
                    f"{int(user_id):06d}-"
                    f"{random_code}"
                )

                conn.execute("""
                    INSERT INTO language_certificates
                    (
                        user_id,
                        language,
                        certificate_id
                    )
                    VALUES (?, ?, ?)
                """, (
                    user_id,
                    language,
                    certificate_id
                ))

                conn.commit()

                cert = conn.execute("""
                    SELECT
                        certificate_id,
                        issued_at
                    FROM language_certificates
                    WHERE user_id = ?
                    AND language = ?
                """, (
                    user_id,
                    language
                )).fetchone()

            certificates[language] = cert

        # ----------------------------------------------------
        # OVERALL TOTAL
        # ----------------------------------------------------

        total_row = conn.execute("""
            SELECT COUNT(DISTINCT problem_id) AS total
            FROM user_problem_progress
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        total_solved = (
            total_row["total"]
            if total_row
            else 0
        )

        # ----------------------------------------------------
        # RENDER PAGE
        # ----------------------------------------------------

        return render_template(
            "certificate.html",

            user=user,

            progress=progress,

            certificates=certificates,

            total_solved=total_solved
        )

    finally:

        conn.close()

    # ============================================================
# CREATE / GET CERTIFICATE
# ============================================================

def ensure_certificate(user_id):

    db = get_db()
    cursor = db.cursor()

    # Check whether certificate already exists
    cursor.execute("""
        SELECT certificate_id, issued_at
        FROM certificates
        WHERE user_id = ?
    """, (user_id,))

    existing = cursor.fetchone()

    if existing:
        return {
            "certificate_id": existing["certificate_id"],
            "issued_at": existing["issued_at"]
        }

    # Check total solved problems
    cursor.execute("""
        SELECT COUNT(DISTINCT problem_id)
        FROM user_problem_progress
        WHERE user_id = ?
    """, (user_id,))

    total_solved = cursor.fetchone()[0]

    # Certificate unlock condition
    if total_solved < 135:
        return None

    # Generate unique certificate ID
    year = datetime.now().year

    certificate_id = (
        f"CM-{year}-{user_id:05d}-"
        f"{uuid.uuid4().hex[:6].upper()}"
    )

    cursor.execute("""
        INSERT INTO certificates
        (user_id, certificate_id)
        VALUES (?, ?)
    """, (
        user_id,
        certificate_id
    ))

    db.commit()

    cursor.execute("""
        SELECT certificate_id, issued_at
        FROM certificates
        WHERE user_id = ?
    """, (user_id,))

    certificate = cursor.fetchone()

    return {
        "certificate_id": certificate["certificate_id"],
        "issued_at": certificate["issued_at"]
    }
# ==========================================
# Logout
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!")

    return redirect(url_for("home"))


# ==========================================
# Error Pages
# ==========================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template("500.html"), 500
    # ==========================================
# Online Compiler API
# Part 3A
# Python + JavaScript
# ==========================================
@app.route("/run", methods=["POST"])
def run_code():

    data = request.get_json()

    language = data.get("language", "").lower()
    code = data.get("code", "")
    user_input = data.get("input", "")

    try:

        # Python
        if language == "python":

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".py",
                mode="w",
                encoding="utf-8"
            ) as f:
                f.write(code)
                filename = f.name

            result = subprocess.run(
                ["python", filename],
                input=user_input,
                text=True,
                capture_output=True,
                timeout=5
            )

            os.remove(filename)

            return jsonify({
                "output": result.stdout,
                "error": result.stderr
            })

        # C
        elif language == "c":

            c_file = "main.c"
            exe_file = f"{uuid.uuid4().hex}.exe"

            with open(c_file, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["gcc", c_file, "-o", exe_file],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return jsonify({
                    "output": "",
                    "error": compile_result.stderr
                })

            result = subprocess.run(
                [exe_file],
                input=user_input,
                text=True,
                capture_output=True,
                timeout=5,
                shell=True
            )

            return jsonify({
                "output": result.stdout,
                "error": result.stderr
            })
        # Java
        elif language == "java":

            java_file = "Main.java"

            with open(java_file, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return jsonify({
                    "output": "",
                    "error": compile_result.stderr
                })

            result = subprocess.run(
                ["java", "Main"],
                input=user_input,
                text=True,
                capture_output=True,
                timeout=5
            )

            return jsonify({
                "output": result.stdout,
                "error": result.stderr
            })

        # C++
        elif language == "cpp":

            cpp_file = "main.cpp"
            exe_file = f"{uuid.uuid4().hex}.exe"

            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["g++", cpp_file, "-o", exe_file],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return jsonify({
                    "output": "",
                    "error": compile_result.stderr
                })

            result = subprocess.run(
                [exe_file],
                input=user_input,
                text=True,
                capture_output=True,
                timeout=5,
                shell=True
            )

            return jsonify({
                "output": result.stdout,
                "error": result.stderr
            })

        else:
            return jsonify({
                "output": "",
                "error": "Unsupported language"
            })

    except subprocess.TimeoutExpired:
        return jsonify({
            "output": "",
            "error": "Time Limit Exceeded (5 seconds)"
        })

    except FileNotFoundError as e:
        return jsonify({
            "output": "",
            "error": f"Compiler not found: {str(e)}"
        })

    except Exception as e:
        return jsonify({
            "output": "",
            "error": str(e)
        })

    finally:

        files_to_delete = [
            "main.c",
            "Main.java",
            "Main.class",
            "main.cpp",
            "main.exe"
        ]

        for file in files_to_delete:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

            # ==========================================
    

# ==========================================
# Test Mail
# ==========================================

@app.route("/test-mail")
def test_mail():

    msg = Message(
        "Test Mail",
        recipients=["mee_gmail@gmail.com"]
    )

    msg.body = "Testing Flask Mail"

    mail.send(msg)

    return "Mail Sent Successfully"


# ==========================================
# Health Check
# ==========================================


    
# ==========================================
# Health Check
# ==========================================

@app.route("/health")
def health():

    return jsonify({
        "status": "success",
        "message": "CodeMaster Server is Running"
    })


@app.route("/save_user_code", methods=["POST"])
def save_user_code():

    if not session.get("logged_in") or not session.get("user_id"):
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json() or {}

    problem_id = data.get("problem_id")
    language = data.get("language", "python").lower()
    code = data.get("code", "")

    try:
        problem_id = int(problem_id)
    except:
        return jsonify({
            "success": False,
            "message": "Invalid problem ID."
        }), 400

    user_id = session["user_id"]

    conn = get_db_connection()

    try:

        conn.execute(
            """
            INSERT INTO user_problem_codes
            (
                user_id,
                problem_id,
                language,
                code,
                updated_at
            )
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(user_id, problem_id, language)
            DO UPDATE SET
                code = excluded.code,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                problem_id,
                language,
                code
            )
        )

        conn.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:

        conn.rollback()

        print(
            "SAVE USER CODE ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        conn.close()


@app.route("/get_user_code/<int:problem_id>")
def get_user_code(problem_id):

    if not session.get("logged_in") or not session.get("user_id"):
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    language = request.args.get(
        "language",
        "python"
    ).lower()

    conn = get_db_connection()

    row = conn.execute(
        """
        SELECT code
        FROM user_problem_codes
        WHERE user_id = ?
        AND problem_id = ?
        AND language = ?
        """,
        (
            user_id,
            problem_id,
            language
        )
    ).fetchone()

    conn.close()

    if row:

        return jsonify({
            "success": True,
            "code": row["code"]
        })

    return jsonify({
        "success": True,
        "code": ""
    })

# ============================================================
# CODEMASTER - SEPARATE CODE EXECUTION ROUTE
# Endpoint: /execute_code
# No 5-second time limit
# ============================================================

@app.route("/execute_code", methods=["POST"])
def execute_code():

    data = request.get_json(silent=True) or {}

    language = str(
        data.get("language", "python")
    ).strip().lower()

    code = str(
        data.get("code", "")
    )

    user_input = str(
        data.get("input", "")
    )


    if not code.strip():

        return jsonify({
            "success": False,
            "output": "",
            "error": "Please write your code first."
        }), 400


    temp_dir = None


    try:

        # ====================================================
        # PYTHON
        # ====================================================

        if language in ("python", "py"):

            temp_dir = tempfile.mkdtemp(
                prefix="codemaster_python_"
            )

            source_file = os.path.join(
                temp_dir,
                "main.py"
            )


            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(code)


            result = subprocess.run(
                [
                    sys.executable,
                    source_file
                ],
                input=user_input,
                text=True,
                capture_output=True
                # NO timeout
            )


            return jsonify({
                "success":
                    result.returncode == 0,

                "status":
                    "executed"
                    if result.returncode == 0
                    else "runtime_error",

                "output":
                    result.stdout.strip(),

                "error":
                    result.stderr.strip()
            })


        # ====================================================
        # C
        # ====================================================

        elif language == "c":

            temp_dir = tempfile.mkdtemp(
                prefix="codemaster_c_"
            )

            source_file = os.path.join(
                temp_dir,
                "main.c"
            )

            executable_file = os.path.join(
                temp_dir,
                "main.exe"
            )


            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(code)


            compile_result = subprocess.run(
                [
                    "gcc",
                    source_file,
                    "-o",
                    executable_file
                ],
                capture_output=True,
                text=True
            )


            if compile_result.returncode != 0:

                return jsonify({
                    "success": False,
                    "status": "compile_error",
                    "output": "",
                    "error":
                        compile_result.stderr
                })


            result = subprocess.run(
                [
                    executable_file
                ],
                input=user_input,
                text=True,
                capture_output=True
                # NO timeout
            )


            return jsonify({
                "success":
                    result.returncode == 0,

                "status":
                    "executed"
                    if result.returncode == 0
                    else "runtime_error",

                "output":
                    result.stdout.strip(),

                "error":
                    result.stderr.strip()
            })


        # ====================================================
        # C++
        # ====================================================

        elif language in ("cpp", "c++"):

            temp_dir = tempfile.mkdtemp(
                prefix="codemaster_cpp_"
            )

            source_file = os.path.join(
                temp_dir,
                "main.cpp"
            )

            executable_file = os.path.join(
                temp_dir,
                "main.exe"
            )


            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(code)


            compile_result = subprocess.run(
                [
                    "g++",
                    source_file,
                    "-o",
                    executable_file
                ],
                capture_output=True,
                text=True
            )


            if compile_result.returncode != 0:

                return jsonify({
                    "success": False,
                    "status": "compile_error",
                    "output": "",
                    "error":
                        compile_result.stderr
                })


            result = subprocess.run(
                [
                    executable_file
                ],
                input=user_input,
                text=True,
                capture_output=True
                # NO timeout
            )


            return jsonify({
                "success":
                    result.returncode == 0,

                "status":
                    "executed"
                    if result.returncode == 0
                    else "runtime_error",

                "output":
                    result.stdout.strip(),

                "error":
                    result.stderr.strip()
            })


        # ====================================================
        # JAVA
        # ====================================================

        elif language == "java":

            temp_dir = tempfile.mkdtemp(
                prefix="codemaster_java_"
            )

            source_file = os.path.join(
                temp_dir,
                "Main.java"
            )


            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(code)


            compile_result = subprocess.run(
                [
                    "javac",
                    source_file
                ],
                capture_output=True,
                text=True
            )


            if compile_result.returncode != 0:

                return jsonify({
                    "success": False,
                    "status": "compile_error",
                    "output": "",
                    "error":
                        compile_result.stderr
                })


            result = subprocess.run(
                [
                    "java",
                    "-cp",
                    temp_dir,
                    "Main"
                ],
                input=user_input,
                text=True,
                capture_output=True
                # NO timeout
            )


            return jsonify({
                "success":
                    result.returncode == 0,

                "status":
                    "executed"
                    if result.returncode == 0
                    else "runtime_error",

                "output":
                    result.stdout.strip(),

                "error":
                    result.stderr.strip()
            })


        # ====================================================
        # UNSUPPORTED LANGUAGE
        # ====================================================

        return jsonify({
            "success": False,
            "status": "error",
            "output": "",
            "error":
                "Unsupported language: " +
                language
        }), 400


    except FileNotFoundError as e:

        return jsonify({
            "success": False,
            "status": "error",
            "output": "",
            "error":
                "Compiler/interpreter not found: " +
                str(e)
        }), 500


    except Exception as e:

        return jsonify({
            "success": False,
            "status": "error",
            "output": "",
            "error": str(e)
        }), 500


    finally:

        # ====================================================
        # DELETE TEMPORARY DIRECTORY
        # ====================================================

        if temp_dir:

            try:

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

            except Exception:

                pass
@app.route("/clear_user_code", methods=["POST"])
def clear_user_code():

    if not session.get("logged_in") or not session.get("user_id"):
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json() or {}

    problem_id = data.get("problem_id")
    language = data.get(
        "language",
        "python"
    ).lower()

    user_id = session["user_id"]

    conn = get_db_connection()

    try:

        conn.execute(
            """
            DELETE FROM user_problem_codes
            WHERE user_id = ?
            AND problem_id = ?
            AND language = ?
            """,
            (
                user_id,
                problem_id,
                language
            )
        )

        conn.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:

        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        conn.close()

@app.route("/check_problem_status/<int:problem_id>")
def check_problem_status(problem_id):

    if "user_id" not in session:
        return jsonify({
            "solved": False
        }), 401

    user_id = session["user_id"]

    conn = get_db()

    row = conn.execute(
        """
        SELECT 1
        FROM user_solved_problems
        WHERE user_id = ?
        AND problem_id = ?
        LIMIT 1
        """,
        (
            user_id,
            problem_id
        )
    ).fetchone()

    conn.close()

    return jsonify({
        "solved": row is not None
    })

@app.route("/check_solved/<int:problem_id>")
def check_solved(problem_id):

    if not session.get("logged_in") or not session.get("user_id"):
        return jsonify({
            "success": False,
            "solved": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    conn = get_db_connection()

    row = conn.execute("""
        SELECT id
        FROM user_solved_problems
        WHERE user_id = ?
        AND problem_id = ?
        LIMIT 1
    """, (
        user_id,
        problem_id
    )).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "solved": row is not None
    })


def reset_contests_for_testing():

    conn = get_db_connection()

    try:

        now = datetime.now()


        contests_data = [

            # ==================================
            # 1. LIVE
            # ==================================

            (
                "Weekly Coding Challenge",
                "Weekly Coding Challenge",
                "Compete, solve problems and climb the leaderboard.",
                now - timedelta(minutes=30),
                now + timedelta(hours=1, minutes=30),
                "live",
                1250
            ),


            # ==================================
            # 2. UPCOMING
            # ==================================

            (
                "Monthly Challenge",
                "Monthly Challenge",
                "Solve challenging programming problems in our monthly contest.",
                now + timedelta(hours=2),
                now + timedelta(hours=5),
                "upcoming",
                850
            ),


            # ==================================
            # 3. FINISHED
            # ==================================

            (
                "Algorithm Contest",
                "Algorithm Contest",
                "Test your algorithmic thinking and problem solving skills.",
                now - timedelta(days=1, hours=3),
                now - timedelta(days=1),
                "finished",
                1600
            ),


            # ==================================
            # 4. LIVE
            # ==================================

            (
                "Python Speed Challenge",
                "Python Speed Challenge",
                "Solve Python programming challenges against the clock.",
                now - timedelta(minutes=10),
                now + timedelta(hours=2),
                "live",
                620
            ),


            # ==================================
            # 5. UPCOMING
            # ==================================

            (
                "Data Structures Challenge",
                "Data Structures Challenge",
                "Challenge yourself with arrays, trees, graphs and algorithms.",
                now + timedelta(hours=4),
                now + timedelta(hours=7),
                "upcoming",
                430
            ),


            # ==================================
            # 6. LIVE
            # ==================================

            (
                "CodeMaster Weekly Arena",
                "CodeMaster Weekly Arena",
                "A fast paced programming contest for CodeMaster users.",
                now - timedelta(minutes=20),
                now + timedelta(hours=1),
                "live",
                980
            )

        ]


        # Get existing contest IDs

        rows = conn.execute("""
            SELECT id
            FROM contests
            ORDER BY id ASC
            LIMIT 6
        """).fetchall()


        # If less than 6 exist, create them

        while len(rows) < 6:

            conn.execute("""
                INSERT INTO contests
                (
                    title,
                    name,
                    description,
                    duration,
                    start_time,
                    end_time,
                    status,
                    participants
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "New Coding Contest",
                "New Coding Contest",
                "Coding contest",
                120,
                now.strftime("%Y-%m-%d %H:%M:%S"),
                (
                    now + timedelta(hours=2)
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "live",
                0
            ))

            conn.commit()


            rows = conn.execute("""
                SELECT id
                FROM contests
                ORDER BY id ASC
                LIMIT 6
            """).fetchall()


        # ==================================
        # UPDATE FIRST 6
        # ==================================

        for index, row in enumerate(rows[:6]):

            contest = contests_data[index]

            (
                title,
                name,
                description,
                start_time,
                end_time,
                status,
                participants
            ) = contest


            conn.execute("""
                UPDATE contests
                SET
                    title = ?,
                    name = ?,
                    description = ?,
                    duration = ?,
                    start_time = ?,
                    end_time = ?,
                    status = ?,
                    participants = ?
                WHERE id = ?
            """, (

                title,
                name,
                description,
                120,
                start_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                end_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                status,
                participants,
                row["id"]

            ))


        conn.commit()


        print()
        print("========================================")
        print(" CONTEST DATA RESET")
        print("========================================")
        print(" LIVE      : 3")
        print(" UPCOMING  : 2")
        print(" FINISHED  : 1")
        print(" TOTAL     : 6")
        print("========================================")
        print()


    finally:

        conn.close()
# =====================================================
# SUBMIT SOLUTION
# =====================================================
@app.route("/submit_solution", methods=["POST"])
def submit_solution():

    temp_dir = None
    conn = None

    try:
        # =====================================================
        # LOGIN CHECK
        # =====================================================
        if not session.get("logged_in") or not session.get("user_id"):
            return jsonify({
                "success": False,
                "status": "login_required",
                "message": "Please login before submitting."
            }), 401

        user_id = session.get("user_id")

        # =====================================================
        # GET FRONTEND DATA
        # =====================================================
        data = request.get_json(silent=True) or {}

        code = str(data.get("code", "")).strip()
        language = str(data.get("language", "python")).lower().strip()
        user_input = str(data.get("input", "") or "")

        try:
            problem_id = int(data.get("problem_id", 1))
        except Exception:
            return jsonify({
                "success": False,
                "status": "server_error",
                "message": "Invalid problem ID."
            }), 400

        # =====================================================
        # CODE CHECK
        # =====================================================
        if not code:
            return jsonify({
                "success": False,
                "status": "wrong",
                "message": "Please write your code."
            }), 400

        supported_languages = [
            "python",
            "c",
            "cpp",
            "java"
        ]

        if language not in supported_languages:
            return jsonify({
                "success": False,
                "status": "server_error",
                "message": f"Unsupported language: {language}"
            }), 400

        # =====================================================
        # DATABASE
        # =====================================================
        conn = get_db_connection()

        # =====================================================
        # SAVE USER CODE
        # =====================================================
        try:
            conn.execute("""
                INSERT INTO user_problem_codes
                (
                    user_id,
                    problem_id,
                    language,
                    code,
                    updated_at
                )
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)

                ON CONFLICT(user_id, problem_id, language)
                DO UPDATE SET
                    code = excluded.code,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                user_id,
                problem_id,
                language,
                code
            ))

            conn.commit()

        except Exception as e:
            conn.rollback()

            print("USER CODE SAVE ERROR:", e)

            return jsonify({
                "success": False,
                "status": "server_error",
                "message": "Unable to save your code.",
                "error": str(e)
            }), 500

        # =====================================================
        # EXPECTED OUTPUTS
        # =====================================================
        expected_answers = {
            1: "[0, 1]",
            2: "5",
            3: "True",
            4: "6",
            5: "[1, 3, 12, 0, 0]",
            6: "[24,12,8,6]",
            7: "[[-1,-1,2],[-1,0,1]]",
            8: "49",
            9: "2",
            10: "[5,6,7,1,2,3,4]",
            11: "6",
            12: "2",
            13: "6",
            14: "[3,3,5,5,6,7]",
            15: "2.0",
            16: "True",
            17: "True",
            18: "f1",
            19: '["o","l","l","e","h"]',
            20: "0",
            21: "3",
            22: '[["eat","tea","ate"],["tan","nat"],["bat"]]',
            23: "bab",
            24: "-42",
            25: "true",
            26: "BANC",
            27: "true",
            28: '["cats and dog","cat sand dog"]',
            29: "3",
            30: "3",
            31: "true",
            32: "321",
            33: '["1","2","Fizz","4","Buzz"]',
            34: "4",
            35: "true",
            36: "1024.0",
            37: "true",
            38: "36",
            39: "6",
            40: "3",
            41: "3",
            42: "4",
            43: "7",
            44: "MCMXCIV",
            45: "6",
            46: "[5,4,3,2,1]",
            47: "[1,1,2,3,4,4]",
            48: "true",
            49: "[1,2,3]",
            50: "[3,4,5]",
            51: "[7,0,8]",
            52: "[1,2,3,5]",
            53: "[1,4,2,3]",
            54: "deep copy of the linked list",
            55: "[1,2,3,4]",
            56: "[1,1,2,3,4,5,6]",
            57: "[2,1,4,3,5]",
            58: "-1",
            59: "true",
            60: "8",
            61: "true",
            62: "-3",
            63: "2",
            64: "ca",
            65: "true",
            66: "[1,4,2,1,1,0,0]",
            67: "9",
            68: "accaccacc",
            69: "/home/bar",
            70: "[4,2,4,-1,-1]",
            71: "10",
            72: "6",
            73: "-4",
            74: "9",
            75: "acdb",
            76: "1",
            77: "[1,2,1]",
            78: "false",
            79: "[1.0,5.5,4.6667]",
            80: "6",
            81: "4",
            82: "6",
            83: "3",
            84: "Dire",
            85: "8",
            86: "[3,3,5,5,6,7]",
            87: "3",
            88: "37",
            89: "7",
            90: "3",
            91: "3",
            92: "true",
            93: "[4,7,2,9,6,3,1]",
            94: "true",
            95: "[[3],[9,20],[15,7]]",
            96: "true",
            97: "3",
            98: "[3,9,20,null,null,15,7]",
            99: "[1,3,4]",
            100: "1",
            101: "42",
            102: "restored tree equivalent",
            103: "[2,1,4,null,null,3]",
            104: "[[9],[3,15],[20],[7]]",
            105: "6",
            106: "true",
            107: "[[2,2,2],[2,2,0],[2,2,2]]",
            108: "3",
            109: "2",
            110: "2",
            111: "cloned graph",
            112: "true",
            113: "4",
            114: "[[0,2],[1,0],[1,1],[1,2],[2,0],[2,1]]",
            115: "2",
            116: "5",
            117: "wertf",
            118: "[[1,3]]",
            119: '["JFK","MUC","LHR","SFO","SJC"]',
            120: "20",
            121: "8",
            122: "8",
            123: "12",
            124: "15",
            125: "[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]",
            126: "3",
            127: "4",
            128: "28",
            129: "true",
            130: "true",
            131: "5",
            132: "3",
            133: "167",
            134: "true",
            135: "120"
        }

        expected_output = str(
            expected_answers.get(problem_id, "")
        ).strip()

        # =====================================================
        # DEFAULT EXAMPLE INPUTS
        # =====================================================
        #
        # IMPORTANT:
        # If frontend does not send input, these examples
        # prevent EOFError for the currently supported problems.
        #
        # =====================================================

        default_inputs = {

            # Two Sum
            1: "2 7 11 15\n9\n",

            # Longest Consecutive Sequence
            2: "100 4 200 1 3 2\n",

            # Contains Duplicate
            3: "1 2 3 1\n",

            # Maximum Subarray
            4: "-2 1 -3 4 -1 2 1 -5 4\n",

            # Product Except Self
            5: "1 2 3 4\n",

            # Move Zeroes
            6: "1 2 3 4\n",

            # 3Sum
            7: "-1 0 1 2 -1 -4\n",

            # Container With Most Water
            8: "1 8 6 2 5 4 8 3 7\n",

            # First Missing Positive
            9: "3 4 -1 1\n",

            # Rotate Array
            10: "1 2 3 4 5 6 7\n3\n",

            # Best Time to Buy and Sell Stock
            11: "7 1 5 3 6 4\n",

            # Binary Search
            12: "-1 0 3 5 9 12\n9\n",

            # Search Insert Position
            13: "1 3 5 6\n5\n",

            # Merge Intervals
            14: "1 3\n2 6\n8 10\n15 18\n",

            # Median of Two Sorted Arrays
            15: "1 3\n2\n",

            # Permutation in String
            16: "ab\neidbaooo\n",

            # Valid Anagram
            17: "anagram\nnagaram\n",

            # First Unique Character
            18: "leetcode\n",

            # Reverse String
            19: "hello\n",

            # Majority Element
            20: "2 2 1 1 1 2 2\n"
        }

        if not user_input.strip():
            user_input = default_inputs.get(
                problem_id,
                ""
            )

        # =====================================================
        # CONTEST MODE
        # =====================================================
        contest_mode = bool(data.get("contest_mode", False))
        contest_id = data.get("contest_id")

        if contest_mode:

            if not contest_id:
                return jsonify({
                    "success": False,
                    "status": "server_error",
                    "message": "Contest ID is required."
                }), 400

            cursor = conn.cursor()

            # -------------------------------------------------
            # CONTEST
            # -------------------------------------------------
            cursor.execute("""
                SELECT *
                FROM contests
                WHERE id = ?
            """, (contest_id,))

            contest = cursor.fetchone()

            if not contest:
                return jsonify({
                    "success": False,
                    "status": "server_error",
                    "message": "Contest not found."
                }), 404

            # -------------------------------------------------
            # PARTICIPANT
            # -------------------------------------------------
            cursor.execute("""
                SELECT *
                FROM contest_participants
                WHERE contest_id = ?
                AND user_id = ?
            """, (
                contest_id,
                user_id
            ))

            participant = cursor.fetchone()

            if not participant:
                return jsonify({
                    "success": False,
                    "status": "server_error",
                    "message":
                        "You are not registered for this contest."
                }), 403

            # -------------------------------------------------
            # CONTEST PROBLEM
            # -------------------------------------------------
            cursor.execute("""
                SELECT points
                FROM contest_problems
                WHERE contest_id = ?
                AND problem_id = ?
            """, (
                contest_id,
                problem_id
            ))

            contest_problem = cursor.fetchone()

            if not contest_problem:
                return jsonify({
                    "success": False,
                    "status": "server_error",
                    "message":
                        "This problem is not part of the contest."
                }), 403

            # -------------------------------------------------
            # CONTEST TIME
            # -------------------------------------------------
            try:
                now = datetime.now()

                start_value = contest["start_time"]
                end_value = contest["end_time"]

                if isinstance(start_value, str):
                    start_time = datetime.strptime(
                        start_value,
                        "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    start_time = start_value

                if isinstance(end_value, str):
                    end_time = datetime.strptime(
                        end_value,
                        "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    end_time = end_value

                if now < start_time:
                    return jsonify({
                        "success": False,
                        "status": "server_error",
                        "message":
                            "Contest has not started yet."
                    }), 403

                if now >= end_time:
                    return jsonify({
                        "success": False,
                        "status": "server_error",
                        "message":
                            "Contest has ended."
                    }), 403

            except Exception as e:
                print("CONTEST TIME ERROR:", e)

        # =====================================================
        # TEMP DIRECTORY
        # =====================================================
        temp_dir = tempfile.mkdtemp(
            prefix="codemaster_"
        )

        source_file = None
        executable_file = None
        run_result = None

        # =====================================================
        # PYTHON
        # =====================================================
        if language == "python":

            source_file = os.path.join(
                temp_dir,
                "main.py"
            )

            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(code)

            # -------------------------------------------------
            # IMPORTANT FIX:
            # input=user_input prevents EOFError
            # -------------------------------------------------
            run_result = subprocess.run(
                [
                    sys.executable,
                    source_file
                ],
                input=user_input,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

        # =====================================================
        # C
        # =====================================================
        elif language == "c":

            c_base_dir = RUN_FOLDER

            os.makedirs(
                c_base_dir,
                exist_ok=True
            )

            temp_dir = tempfile.mkdtemp(
                prefix="c_",
                dir=c_base_dir
            )

            source_file = os.path.join(
                temp_dir,
                "main.c"
            )

            executable_file = os.path.join(
                temp_dir,
                "main.exe"
            )

            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(code)

            compile_result = subprocess.run(
                [
                    "gcc",
                    source_file,
                    "-o",
                    executable_file
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if compile_result.returncode != 0:
                return jsonify({
                    "success": False,
                    "status": "error",
                    "message": "C Compilation Error",
                    "error": compile_result.stderr,
                    "expected_output": expected_output
                }), 200

            if not os.path.exists(executable_file):
                return jsonify({
                    "success": False,
                    "status": "error",
                    "message":
                        "C executable was not created.",
                    "expected_output": expected_output
                }), 200

            run_result = subprocess.run(
                [
                    executable_file
                ],
                input=user_input,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

        # =====================================================
        # C++
        # =====================================================
        elif language == "cpp":

            cpp_base_dir = RUN_FOLDER

            os.makedirs(
                cpp_base_dir,
                exist_ok=True
            )

            temp_dir = tempfile.mkdtemp(
                prefix="cpp_",
                dir=cpp_base_dir
            )

            source_file = os.path.join(
                temp_dir,
                "main.cpp"
            )

            executable_file = os.path.join(
                temp_dir,
                "main.exe"
            )

            with open(
                source_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(code)

            compile_result = subprocess.run(
                [
                    "g++",
                    source_file,
                    "-std=c++17",
                    "-o",
                    executable_file
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if compile_result.returncode != 0:
                return jsonify({
                    "success": False,
                    "status": "error",
                    "message":
                        "C++ Compilation Error",
                    "error":
                        compile_result.stderr,
                    "expected_output":
                        expected_output
                }), 200

            if not os.path.exists(executable_file):
                return jsonify({
                    "success": False,
                    "status": "error",
                    "message":
                        "C++ executable was not created.",
                    "expected_output":
                        expected_output
                }), 200

            run_result = subprocess.run(
                [
                    executable_file
                ],
                input=user_input,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

        # =====================================================
        # JAVA
        # =====================================================
        elif language == "java":

            java_file = os.path.join(
                temp_dir,
                "Main.java"
            )

            with open(
                java_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(code)

            compile_result = subprocess.run(
                [
                    "javac",
                    "Main.java"
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if compile_result.returncode != 0:
                return jsonify({
                    "success": False,
                    "status": "error",
                    "message":
                        "Java Compilation Error",
                    "error":
                        compile_result.stderr,
                    "expected_output":
                        expected_output
                }), 200

            class_file = os.path.join(
                temp_dir,
                "Main.class"
            )

            if not os.path.exists(class_file):
                return jsonify({
                    "success": False,
                    "status": "error",
                    "message":
                        "Main.class was not created.",
                    "expected_output":
                        expected_output
                }), 200

            run_result = subprocess.run(
                [
                    "java",
                    "-cp",
                    ".",
                    "Main"
                ],
                input=user_input,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

        # =====================================================
        # SAFETY CHECK
        # =====================================================
        if run_result is None:
            return jsonify({
                "success": False,
                "status": "server_error",
                "message": "Program was not executed."
            }), 500

        # =====================================================
        # RUNTIME ERROR
        # =====================================================
        if run_result.returncode != 0:

            error_text = (
                run_result.stderr.strip()
                or "Program exited with an error."
            )

            return jsonify({
                "success": False,
                "status": "error",
                "message": "Compilation / Runtime Error",
                "error": error_text,
                "expected_output": expected_output,
                "actual_output":
                    run_result.stdout.strip()
            }), 200

        # =====================================================
        # OUTPUT
        # =====================================================
        output = run_result.stdout.strip()

        # =====================================================
        # NORMALIZE OUTPUT
        # =====================================================
        def normalize_output(value):

            value = str(value).strip()

            # Remove surrounding spaces
            value = value.strip()

            # Normalize booleans
            if value.lower() == "true":
                return "true"

            if value.lower() == "false":
                return "false"

            # Remove spaces around commas
            value = re.sub(
                r"\s*,\s*",
                ",",
                value
            )

            # Remove spaces after [
            value = re.sub(
                r"\[\s+",
                "[",
                value
            )

            # Remove spaces before ]
            value = re.sub(
                r"\s+\]",
                "]",
                value
            )

            # Normalize newlines/spaces
            value = " ".join(
                value.split()
            )

            # Python quotes vs JSON quotes
            value = value.replace(
                "'",
                '"'
            )

            return value

        actual_normalized = normalize_output(
            output
        )

        expected_normalized = normalize_output(
            expected_output
        )

        # =====================================================
        # PRINT DEBUG
        # =====================================================
        print("=" * 50)
        print("PROBLEM ID:", problem_id)
        print("USER ID:", user_id)
        print("LANGUAGE:", language)
        print("INPUT:", repr(user_input))
        print("EXPECTED:", expected_output)
        print("ACTUAL:", output)
        print("NORMALIZED EXPECTED:", expected_normalized)
        print("NORMALIZED ACTUAL:", actual_normalized)
        print("=" * 50)

        # =====================================================
        # CORRECT
        # =====================================================
        if actual_normalized == expected_normalized:

            solved_insert = conn.execute("""
                INSERT OR IGNORE INTO user_solved_problems
                (
                    user_id,
                    problem_id,
                    solved_at
                )
                VALUES (
                    ?,
                    ?,
                    datetime('now')
                )
            """, (
                user_id,
                problem_id
            ))

            # -------------------------------------------------
            # FIRST TIME SOLVED
            # -------------------------------------------------
            if solved_insert.rowcount == 1:

                problem_data = conn.execute("""
                    SELECT difficulty
                    FROM problems
                    WHERE id = ?
                """, (
                    problem_id,
                )).fetchone()

                rating_points = 0

                if problem_data:

                    difficulty = str(
                        problem_data["difficulty"]
                    ).strip().lower()

                    if difficulty == "easy":
                        rating_points = 10

                    elif difficulty == "medium":
                        rating_points = 20

                    elif difficulty == "hard":
                        rating_points = 30

                # -------------------------------------------------
                # UPDATE USER
                # -------------------------------------------------
                conn.execute("""
                    UPDATE users
                    SET
                        solved = COALESCE(solved, 0) + 1,
                        rating = COALESCE(rating, 0) + ?
                    WHERE id = ?
                """, (
                    rating_points,
                    user_id
                ))

            # -------------------------------------------------
            # PROGRESS
            # -------------------------------------------------
            try:

                normalized_language = normalize_language(
                    language
                )

                conn.execute("""
                    INSERT OR IGNORE INTO user_problem_progress
                    (
                        user_id,
                        problem_id,
                        language
                    )
                    VALUES (?, ?, ?)
                """, (
                    user_id,
                    problem_id,
                    normalized_language
                ))

            except Exception as progress_error:

                print(
                    "PROGRESS SAVE ERROR:",
                    progress_error
                )

            conn.commit()

            # =================================================
            # CONTEST ACCEPTED SUBMISSION
            # =================================================
            if contest_mode and contest_id:

                try:

                    # Save accepted contest submission
                    conn.execute("""
                        INSERT INTO contest_submissions
                        (
                            contest_id,
                            user_id,
                            problem_id,
                            language,
                            code,
                            status,
                            submitted_at
                        )
                        VALUES (
                            ?, ?, ?, ?, ?, ?,
                            datetime('now')
                        )
                    """, (
                        contest_id,
                        user_id,
                        problem_id,
                        language,
                        code,
                        "accepted"
                    ))

                    conn.commit()

                except Exception as contest_save_error:

                    print(
                        "CONTEST SUBMISSION SAVE ERROR:",
                        contest_save_error
                    )

                    # Do not fail an otherwise correct answer
                    conn.rollback()

            # =================================================
            # SUCCESS RESPONSE
            # =================================================
            return jsonify({
                "success": True,
                "status": "correct",
                "correct": True,
                "message": "Correct Answer!",
                "output": output,
                "actual_output": output,
                "expected_output": expected_output
            }), 200

        # =====================================================
        # WRONG ANSWER
        # =====================================================
        return jsonify({
            "success": False,
            "status": "wrong",
            "correct": False,
            "message": "Wrong Answer!",
            "output": output,
            "actual_output": output,
            "expected_output": expected_output
        }), 200

    # =====================================================
    # TIME LIMIT
    # =====================================================
    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "status": "timeout",
            "message": "Time Limit Exceeded",
            "error":
                "Your program took more than 5 seconds."
        }), 200

    # =====================================================
    # COMPILER NOT FOUND
    # =====================================================
    except FileNotFoundError as e:

        return jsonify({
            "success": False,
            "status": "error",
            "message":
                "Compiler / interpreter not found.",
            "error":
                str(e)
                + "\n\nPlease install the required compiler "
                  "and add it to PATH."
        }), 200

    # =====================================================
    # SERVER ERROR
    # =====================================================
    except Exception as e:

        print(
            "SUBMIT SOLUTION ERROR:",
            repr(e)
        )

        if conn:

            try:
                conn.rollback()
            except Exception:
                pass

        return jsonify({
            "success": False,
            "status": "server_error",
            "message": str(e)
        }), 500

    # =====================================================
    # CLEANUP
    # =====================================================
    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass

        if temp_dir and os.path.exists(temp_dir):

            try:
                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

            except Exception as cleanup_error:

                print(
                    "TEMP CLEANUP ERROR:",
                    cleanup_error
                )



# ==========================================
# Initialize Database
# ==========================================
# ============================================================
# CODEMASTER DATABASE INITIALIZATION
# ============================================================
create_contest_tables()
with app.app_context():

    print("=" * 60)
    print("Initializing CodeMaster database...")
    print("=" * 60)

    # Main application tables
    create_tables()

    # Contest tables + migrations
   
    print("=" * 60)
    print("CodeMaster database initialization completed.")
    print("=" * 60)


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    create_tables()
    ensure_contest_table()

    seed_contests()

    ensure_contest_registration_table()
    reset_contests_for_testing()

    refresh_contest_status()
   
    print("=" * 60)
    print("🚀 CodeMaster Compiler Server Started")
    print("=" * 60)
    print("Open:")
    print("http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=False
    )
