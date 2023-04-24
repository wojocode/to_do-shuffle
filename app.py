import os
from tempfile import mkdtemp
from cs50 import SQL
from flask import Flask, request, redirect, url_for, render_template,flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

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
    session.clear()
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
            return render_template("index.html")
            
        else:
            flash("Username or password is not correct!","danger")
            return "not okay"
    else:
        return render_template("login.html")
    

@app.route('/logout', methods = ["GET", "POST"])
def logout():   
    session.clear()
    flash("Logout succesfull!", "warning")
    return redirect("/login")

#@app.route('/edit')
#@login_required
#def edit():
    
    
    

    