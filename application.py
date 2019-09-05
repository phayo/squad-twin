from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import random

from helpers import apology, login_required, bestMatch, dominant


# initializing global variables
pers = ["San", "Cho", "Phl", "Mel"]
per = [0, 0, 0, 0]
a = {"san": 1, "cho": 2, "phl": 3, "mel": 4}
b = {"san": 2, "cho": 3, "phl": 4, "mel": 1}
c = {"san": 3, "cho": 4, "phl": 1, "mel": 2}
d = {"san": 4, "cho": 1, "phl": 2, "mel": 3}
UPLOAD_FOLDER = '/static/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def savepersonality(answer):
    for ans in answer:
        if ans == 'a':
            per[0] += a['san']
            per[1] += a['cho']
            per[2] += a['phl']
            per[3] += a['mel']
        elif ans == 'b':
            per[0] += b['san']
            per[1] += b['cho']
            per[2] += b['phl']
            per[3] += b['mel']
        elif ans == 'c':
            per[0] += c['san']
            per[1] += c['cho']
            per[2] += c['phl']
            per[3] += c['mel']
        else:
            per[0] += d['san']
            per[1] += d['cho']
            per[2] += d['phl']
            per[3] += d['mel']
    print(per)
    total = sum(per)
    print(total)
    # finding personality score
    per[0] = round((per[0]/total) * 100)
    per[1] = round((per[1]/total) * 100)
    per[2] = round((per[2]/total) * 100)
    per[3] = round((per[3]/total) * 100)
    answers = "".join(answer)
    # update to personality scores db
    # db.execute("UPDATE users SET (san = :san, cho = :cho, phl = :phl, mel = :mel) WHERE id = userid", 
    #             san=per[0], cho=per[1], phl=per[2], mel=per[3], userid = userid)
    id = db.execute("INSERT INTO users (san, cho, phl, mel, answers) VALUES (:san, :cho, :phl, :mel, :answers)",
                san=per[0], cho=per[1], phl=per[2], mel=per[3], answers=answers)
    # finding personality type
    type = dominant(per)

    # update personality type to db
    db.execute("Update users SET verdict = :type WHERE id = :id", type=type, id=id)
    
    return generateKey(id)

def generateKey(id):
    user = db.execute("SELECT * from users WHERE id = :id", id=id)
    if not len(user) == 1:
        return "Invalid UserId"
    if not user[0]['verdict']:
        return "User has not taken the test"
    b = True
    while b:
        key = random.randint(1111, 9999)
        chk = db.execute("SELECT * FROM users WHERE key = :key", key=key)
        if len(chk) == 0:
            b = False
    db.execute("UPDATE users SET key = :key WHERE id = :id",key=key, id=id)
    return key

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        data = request.get_json()
        
        if not "answers" in data or not "name" in data:
            return apology("Error submitting answers", 400)
        
        answers = data['answers']        
        key = savepersonality(answers)
        print(key)
        return jsonify(key) #render_template("key.html", key=key)
    else:
        questions = db.execute("SELECT * FROM questions")
        return render_template("quiz.html", questions=questions)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("key"):
            return apology("must provide key", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for key
        rows = db.execute("SELECT * FROM users WHERE key = :key AND status = :status",
                          key=request.form.get("key").strip(), status="admin")

        # Ensure key exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid key and/or password", 403)

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
    for i in range(len(all_data)):
        try:
            del all_data[i]["hash"]
        except KeyError:
            print("Key 'testing' not found")

    return render_template("admin.html", data=all_data)

@app.route("/question", methods=["GET", "POST"])
@login_required
def question():
    if request.method == "POST":
        que = request.form.get("que")
        a = request.form.get("a")
        b = request.form.get("b")
        c = request.form.get("c")
        d = request.form.get("d")
        if not que or not a or not b or not c or not d:
            return apology("Fill all inputs", 400)
        db.execute("INSERT INTO questions (question, a , b , c , d) VALUES (:que, :a, :b, :c, :d)",
                    que=que.strip(), a=a.strip(), b=b.strip(), c=c.strip(), d=d.strip())
        return render_template("questions.html", added="added")
    else:
        return render_template("questions.html")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        if not request.form.get("key") or request.form.get("password"):
            return apology("Fill all input fields", 400)
        rows = db.execute("SELECT * FROM users WHERE key = :key", key=request.form.get("key").strip())
        hash = generate_password_hash(request.form.get("password").strip())
        db.execute("UPDATE users SET (hash = :hash, status = :status) WHERE key = :key",
                    hash=hash, status='admin', key=request.form.get("key").strip())
        #session["user_id"] = userid
        return redirect("/dashboard")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/result", methods=["POST"])
def result():
    if request.method == "POST":
        if not request.form.get("key"):
            return apology("Enter a valid key", 400)
        user_row = db.execute("SELECT * FROM users WHERE key = :key", key=request.form.get("key").strip())
        if not len(user_row) == 1:
            return apology("Invalid key", 400)
        verdict = user_row[0]['verdict']

        # find best match
        match = db.execute("SELECT * FROM users WHERE verdict LIKE :type", type=verdict)
        if len(match) == 0:
            match = db.execute("SELECT * FROM users WHERE verdict LIKE %:type%", type=verdict.split("-")[0])
            if len(match) == 0:
                match = db.execute("SELECT * FROM users WHERE verdict LIKE %:type%", type=verdict.split("-")[1])
        
        if len(match) == 1:
            return render_template("result.html", user=user_row[0], match=match[0])
        
        return render_template("result.html", user=user_row[0], match=bestMatch(match, user_row[0]))

@app.route("/key", methods=["POST"])
def key():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files or not request.form.get("name") or not request.form.get("key"):
            return apology("Make sure you filled all inputs and uploaded an image")
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return apology("You have not uploaded an image", 400)
        if file and allowed_file(file.filename):
            actual_filename = request.form.get("key").strip() + "." + file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(actual_filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("UPDATE users SET alias = :alias WHERE key = :key", 
                        alias=request.form.get("name").strip(), key=request.form.get("key"))
            return render_template("key.html", key=request.form.get("key"), alias=request.form.get("name").strip())   





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)