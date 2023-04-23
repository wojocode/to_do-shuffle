import os
from tempfile import mkdtemp
from cs50 import SQL
from flask import Flask, request, redirect, url_for, render_template,flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# configure session (server-side)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#connect database
db = SQL("sqlite:///data.db")

#REGISTER USER#
@app.route('/register', methods=["POST", "GET"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    
    if request.method == "POST":
# ensure proper inputs 
        if not username or not password:
            flash("missing username or password!","danger")
            return render_template('register.html')
        elif password != confirmation:
            flash("password dosn't match!","danger")
            return render_template('register.html')

    # check for free username
        rows = db.execute("SELECT username FROM users WHERE username = ?;",username)
        if len(rows) == 1:
            flash("username is not available!","danger")
            return render_template('register.html')
        else:
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username,hash) VALUES (?,?);", username,hash)
            rows = db.execute("SELECT * FROM users WHERE username = ?;",username)
            session["user_id"] = rows[0]["id"]
            return "okay"
# GET method            
    else:
        return render_template("register.html")
        
        