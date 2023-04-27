import os
from tempfile import mkdtemp
from cs50 import SQL
from flask import Flask, request, redirect, url_for, render_template,flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required,validate_password

app = Flask(__name__)

# configure session (server-side)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#connect database
db = SQL("sqlite:///data.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#REGISTER USER#
@app.route('/register', methods=["POST", "GET"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    
    if request.method == "POST":
# ensure proper inputs 
        if not username or not password:
            flash("Missing username or password!","danger")
            return render_template('register.html')
        elif password != confirmation:
            flash("Password doesn't match!","danger")
            return render_template('register.html')

    # check for free username
        rows = db.execute("SELECT username FROM users WHERE username = ?;",username)
        if len(rows) == 1:
            flash("Username is not available!","danger")
            return render_template('register.html')
        else:
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username,hash) VALUES (?,?);", username,hash)
            rows = db.execute("SELECT * FROM users WHERE username = ?;",username)
            session["user_id"] = rows[0]["id"]
            flash(f"Hello {username} !","success")
            return render_template("index.html")           
    else:
        return render_template("register.html")

        
@app.route('/login', methods = ["POST", "GET"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
# ensure proper inputs
        if not username or not  password:
            flash("Missing username or password!","danger")
            return render_template('login.html')
# check for user 
        rows = db.execute("SELECT * FROM users WHERE username = ?;",username)
        if len(rows) == 1 and check_password_hash(rows[0]["hash"], password):
            session["user_id"] = rows[0]["id"]
            flash(f"Hello {username} !","success")
            return redirect("/")
        else:
            flash("Username or password is not correct!","danger")
            return render_template("login.html")
    else:
        return render_template("login.html")
    

@app.route('/logout', methods = ["GET", "POST"])
def logout():   
    session.clear()
    flash("Logout succesfull!", "warning")
    return redirect("/login")


@app.route('/', methods = ["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
# check inputs 
        task = request.form.get("task")
        category = request.form.get("category")
        date = request.form.get("date")
        if not task or not category or not date:
            flash("Must provide data!","danger")
            return render_template("index.html")
# insert task 
        db.execute("INSERT INTO tasks (task,category,created_date,due_date,user_id) VALUES(?,?,DATE(),?,?);", task,category,date,session["user_id"])
# selecting records and pass it to display 
        rows = db.execute("SELECT task,category,created_date,due_date FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?);",session["user_id"])
# SELECT COUNT of each category
       # house = db.execute("SELECT COUNT(category) AS house FROM tasks GROUP BY category HAVING category = 'Personal' AND user_id IN (SELECT id FROM users WHERE id = ?);",session["user_id"])
        flash("Added task!","success")
        return render_template("index.html",records = rows)
    else:
        rows = db.execute("SELECT task,category,created_date,due_date FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?);",session["user_id"])
        return render_template("index.html", records= rows)
    
@app.route('/edit<task>:<category>:<data>', methods = ["GET", "POST"])
@login_required
def edit(task,category,data):
    if request.method == "POST":
        checked = "checked"
        return render_template("edit.html",task = task, category = category,data = data,checked= checked)  
    else:
        return redirect("/")

#@app.route('/change', methods = ["GET", "POST"])
##def change():
    #if request.method == "POST":
        