from flask import Flask, request, render_template, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3, logging

app = Flask(__name__)
app.secret_key = "change_this_to_something_random"
bcrypt = Bcrypt(app)

logging.basicConfig(filename="/var/log/secure-app/app.log", level=logging.INFO,
                     format="%(message)s")

def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    return conn

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            logging.info(f"REGISTER_SUCCESS user={username} ip={request.remote_addr}")
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username already exists"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        row = conn.execute("SELECT password FROM users WHERE username=?", (username,)).fetchone()
        ip = request.remote_addr

        if row and bcrypt.check_password_hash(row[0], password):
            session["user"] = username
            logging.info(f"LOGIN_SUCCESS user={username} ip={ip}")
            return redirect("/dashboard")
        else:
            logging.warning(f"LOGIN_FAILED user={username} ip={ip}")
            return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return f"Welcome, {session['user']}!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
