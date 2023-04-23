from cs50 import SQL
from flask import Flask, request, redirect, url_for, render_template
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# configure session (server-side)
app.config['SESSION TYPE'] = 'filesystem'
Session(app)

#connect database 
db = SQL("sqlite:///database.db")
