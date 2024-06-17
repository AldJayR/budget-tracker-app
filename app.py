from flask import Flask, redirect, render_template, session, jsonify, flash, request
from flask_session import Session
from cs50 import SQL
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(16))
bcrypt = Bcrypt(app)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///budgets.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect("/")
    
    session.clear()

    if request.method == "POST":
        
        if not request.form.get("email"):
            flash("Please provide a email", "danger")
            return redirect("/login")
        elif not request.form.get("password"):
            flash("Pleae provide a password", "danger")
            return redirect("/login")
        
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        password = rows[0]["password"]

        if len(rows) != 1 or not bcrypt.check_password_hash(password, request.form.get("password")):
            flash("Invalid email or password", "danger")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]  
        
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation or not email:
            flash("Please fill in the required info", "danger")
            return redirect("/register")
        elif password != confirmation:
            flash("Passwords do not match", "danger")
            return redirect("/register")
        
        existing_user = db.execute("SELECT * FROM users WHERE email = ?", email)

        if existing_user:
            flash("Email already taken", "danger")
            return redirect("/register")
        
        hashed_password = bcrypt.generate_password_hash(password)

        db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", username, email, hashed_password)

        return redirect("/")
    else:    
        return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)