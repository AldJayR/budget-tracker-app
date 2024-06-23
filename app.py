from flask import Flask, redirect, render_template, session, jsonify, flash, request, url_for
from flask_session import Session
from cs50 import SQL
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
import secrets
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(16))
bcrypt = Bcrypt(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "jaeczxdev@gmail.com"
app.config["MAIL_PASSWORD"] = "ylap dqwx cnzc bnky"
app.config["MAIL_DEFAULT_SENDER"] = "jaeczxdev@gmail.com"
mail = Mail(app)


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
@login_required
def index():
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])
    users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    
    return render_template("index.html", username=username[0]["username"], transactions=transactions, users=users)

@app.route("/add-transaction/", methods=["POST"])
def add_transaction():
    description = request.form.get("description")
    price = request.form.get("price")
    date = request.form.get("date")

    if not description or not price or not date:
        return jsonify(success=False, error=" Missing data")
    
    try:
        transaction_id = db.execute("INSERT INTO transactions (category, amount, date, user_id) VALUES (?, ?, ?, ?)", description, price, date, session["user_id"])
    except Exception as e:
        return jsonify(success=False, error=str(e))

    new_transaction = db.execute("SELECT * FROM transactions WHERE id = ?", transaction_id)


    if new_transaction:
        return jsonify(success=True, transaction=new_transaction[0])
    else:
        return jsonify(success=False, error="Failed to add transaction")

@app.route("/edit-transaction/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    if request.method == "GET":
        transaction = db.execute("SELECT * FROM transactions WHERE id = ?", transaction_id)

        if transaction:
            return jsonify(success=True, transaction=transaction)
        else:
            return jsonify(success=False, error="Transaction not found")
    else:
        description = request.form.get("description")
        amount = request.form.get("price")
        date = request.form.get("date")

        if not description or not amount or not date:
            return jsonify(success=False, error="Missing data")

        try:
            db.execute("UPDATE transactions SET category = ?, amount = ?, date = ? WHERE id = ?",
                       description, amount, date, transaction_id)
            db.commit()
        except Exception as e:
            return jsonify(success=False, error=str(e))

        updated_transaction = db.execute("SELECT * FROM transactions WHERE id = ?", transaction_id).fetchone()

        if updated_transaction:
            return jsonify(success=True, transaction=updated_transaction)
        else:
            return jsonify(success=False, error="Failed to update transaction")


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

        if rows and bcrypt.check_password_hash(rows[0]["password"], request.form.get("password")):
            if rows[0]["email_verified"] == 1:
                session["user_id"] = rows[0]["id"]  
                return redirect("/")
            else:
                flash("Please verify your email", "danger")
                return redirect("/login")
        else:
            flash("Invalid email or password", "danger")
            print("Hello")
            return redirect("/login")
        
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect("/")


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

        token = secrets.token_urlsafe(20)
        
        hashed_password = bcrypt.generate_password_hash(password)

        db.execute("INSERT INTO users (username, email, password, token) VALUES (?, ?, ?, ?)", username, email, hashed_password, token)

        verification_url = url_for("verify_email", token=token, _external=True)
        send_verification_email(email, verification_url)

        flash("Check your email to get verified", "success")
        return redirect("/register")
    else:    
        return render_template("register.html")

def send_verification_email(email, verification_url):
    msg = Message("Verify Your Email", sender="Jae Dev", recipients=[email])
    msg.body = f"Click the following link to verify your email: {verification_url}"
    mail.send(msg)

@app.route("/verify_email/<token>")
def verify_email(token):
    user = db.execute("SELECT * FROM users WHERE token = ?", token)

    if user:
        db.execute("UPDATE users SET email_verified = ? WHERE token = ?", 1, token)
        flash("Email verified", "success")
    else:
        flash("Invalid verification link", "danger")

    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)