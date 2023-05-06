import os
from tempfile import mkdtemp
from cs50 import SQL
from flask import Flask, request, redirect, url_for, render_template,flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required,validate_password
from random import choice 

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


@app.route('/',)
@login_required
def index():
# display active records 
        rows = db.execute("SELECT task,category,created_date,due_date,id FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        
# pass to html history records 
        history_rows = db.execute("SELECT * FROM archieve INNER JOIN tasks ON tasks.id = archieve.task_id WHERE tasks.user_id = ? AND archieve.status != 'active';",session["user_id"])
        
# SELECT COUNT of each category
        house = db.execute("SELECT COUNT(category) AS house FROM tasks WHERE category = 'House' AND user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        
        work = db.execute("SELECT COUNT(category) AS work FROM tasks WHERE category = 'Work' AND user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        
        personal = db.execute("SELECT COUNT(category) AS personal FROM tasks WHERE category = 'Personal' AND user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        
        return render_template("index.html",records = rows,h = house,w = work,p = personal,hist_row = history_rows)


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
# password validation
        elif validate_password(password) == False:
            flash("Password is too short (at least 8 characters)!","danger")
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
            return redirect("/")           
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
    return redirect("/")
 
        
@app.route('/<category>')
def house(category):
    cat = category
    row = db.execute("SELECT task,category,created_date,due_date,id FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?) AND category = ? AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"],category)
    cat_lower = cat.lower()
    
    if category == "House":
        house = db.execute("SELECT COUNT(category) AS house FROM tasks WHERE category = 'House' AND user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        return render_template("preview.html",records = row,cat = cat, h = house,cat_lower = cat_lower)
        
    elif category == "Work":
        work = db.execute("SELECT COUNT(category) AS work FROM tasks WHERE category = 'Work' AND user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        return render_template("preview.html",records = row,cat = cat, w = work,cat_lower = cat_lower)
      
    elif category == "Personal":  
        personal = db.execute("SELECT COUNT(category) AS personal FROM tasks WHERE category = 'Personal' AND user_id IN (SELECT id FROM users WHERE id = ?) AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
        return render_template("preview.html",records = row,cat = cat, p = personal, cat_lower = cat_lower)
   

### TASK ###
@app.route('/add' ,methods = ["POST", "GET"])
@login_required
def add():
    if request.method == "POST":
        task = request.form.get("task")
        category = request.form.get("category")
        date = request.form.get("date")
        
        if not task or not category or not date:
            flash("Must provide data!","danger")
            return redirect("/")
# insert task 
        db.execute("INSERT INTO tasks (task,category,created_date,due_date,user_id) VALUES(?,?,DATE(),?,?);", task,category,date,session["user_id"])
# keep track of tasks
        id = db.execute("SELECT id FROM tasks WHERE user_id = ? ORDER BY id DESC LIMIT 1",session["user_id"])
        db.execute("INSERT INTO archieve (task_id,status) VALUES (?,'active');",id[0]["id"])
        flash("Added task!","success")
        return redirect("/")


@app.route('/delete<id>', methods = ["POST"])
@login_required
def delete(id):
# update status and set archieved date
    db.execute("UPDATE archieve SET status = 'deleted', archieved = DATE() WHERE task_id = ?;",id )
    flash("Task deleted!","success")
    return redirect('/')


@app.route('/done<id>', methods = ["POST"])
@login_required
def done(id):
    db.execute("UPDATE archieve SET status = 'done', archieved = DATE() WHERE task_id = ? AND task_id IN (SELECT id FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?));",id,session["user_id"])
    flash("Task completed!","success")
    return redirect('/')


@app.route('/done_cat<id>', methods = ["POST"])
@login_required
def done_cat(id):
    db.execute("UPDATE archieve SET status = 'done', archieved = DATE() WHERE task_id = ?;",id )
    #db.execute("DELETE FROM tasks WHERE id = ?",id)
    flash("Task completed!","success")
    return redirect('/')


#UPDATE TASK FROM EDIT PAGE
@app.route('/change<id_user>', methods = ["GET", "POST"])
@login_required
def change(id_user):
    if request.method == "POST":
        task = request.form.get("task")
        category = request.form.get("category")
        date = request.form.get("date")
        db.execute("UPDATE tasks SET task = ?,category = ?,due_date = ? WHERE id = ?;",task,category,date,id_user)
        return redirect(url_for('index'))
    
    
@app.route('/edit<task>:<category>:<data>:<id>', methods = ["GET", "POST"])
@login_required
def edit(task,category,data,id):
    if request.method == "POST":
        checked = "checked"
        return render_template("edit.html",task = task, category = category,data = data,id_number = id, checked = checked)  
    else:
        return redirect("/")
    

@app.route('/history')
@login_required
def history():
        r = db.execute("SELECT * FROM archieve INNER JOIN tasks ON tasks.id = archieve.task_id WHERE tasks.user_id = ? AND archieve.status != 'active';",session["user_id"])
        return render_template('history.html',record = r)
    
    
@app.route('/restore<id>', methods = ["GET", "POST"])
@login_required
def restore(id):
     if request.method == "POST":
        db.execute("UPDATE archieve SET status = 'active' WHERE task_id IN (SELECT id FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?) AND id = ?)",session["user_id"],id)
        return redirect('/')


@app.route('/shuffle')
@login_required
def shuffle():
    r = db.execute("SELECT id FROM tasks WHERE user_id = ? AND id IN (SELECT task_id FROM archieve WHERE status = 'active');",session["user_id"])
# generete random task id 
    shuffle = choice(r)
    number = shuffle["id"]
    rows = db.execute("SELECT task,category,created_date,due_date,id FROM tasks WHERE user_id IN (SELECT id FROM users WHERE id = ?) AND id = ?;", session["user_id"], number)
    return render_template("shuffle.html", records = rows)

@app.route('/clear')
@login_required
def clear():
    db.execute("DELETE FROM archieve WHERE status != 'active' AND task_id IN (SELECT id FROM tasks WHERE user_id = ?);",session["user_id"])
    return redirect('/')