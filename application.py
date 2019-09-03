from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 50
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///squad.db")


@app.route("/")
def index():
    return redirect("/quiz")


@app.route("/quiz", methods=["GET", "POST"])
def quiz()
    if request.method == "POST":
        if not request.form.get("answers") or not request.form.get("name") or not request.form.get("duration"):
            return apology("Error submitting answers",)
        try:
            answers = list(request.form.get("answers"))
            alias = request.form.get("name")
            dur = request.form.get("duration")
        except ValueError:
            #
        
        key = savepersonality(answers, dur, alias)
        render_template("key.html", key=key)
    else:
        questions = db.execute("SELECT * FROM questions")
        render_template("quiz.html", questions=questions)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE alias = :username AND status = :status",
                          username=request.form.get("username").strip(), status="admin")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Show all user data"""
    all_data = db.execute("SELECT * FROM users")
    if (len(all_data) == 0):
        return render_template("empty.html", message="No data to display")

    # format USD values to money
    for i in range(len(history)):
        try:
            del all_data[i]["hash"]
        except KeyError:
            print("Key 'testing' not found")

    return render_template("history.html", data=all_data, l=len(history)))


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        if not request.form.get("key") or request.form.get("password"):
            return apology("Fill all input fields", 400)
        rows = db.execute("SELECT * FROM users WHERE key = :key", key=request.form.get("key").strip())
        hash = generate_password_hash(request.form.get("password").strip())
        db.execute("UPDATE users SET (hash = :hash, status = :status) WHERE key = :key",
                    hash=hash, status='admin' key=request.form.get("key").strip())
        return redirect("/dashboard")
    else:
        render_template("register.html")












def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)