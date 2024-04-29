import os

from cs50 import SQL
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from json import loads
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, lookup

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///moview.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Display the Feed"""
    views = db.execute("SELECT * FROM views INNER JOIN users ON views.user_id = users.id ORDER BY date DESC, time DESC")

    # Get views info into a list
    views_movie_info = []
    for view in views:
        try:
            info_str = lookup(view["imdb_id"], "id")
            info = loads(info_str)
            views_movie_info.append(info)
        except:
            views_movie_info.append(None)

    # Get user infos
    users = db.execute("SELECT * FROM users")


    return render_template("index.html", users=users, views=views, info=views_movie_info, length=len(views))



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", placeholder="Username must be provided")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", placeholder="Password must be provided")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", placeholder="Incorrect username or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        pw_confirmation = request.form.get("confirmation")

        current_users = db.execute("SELECT * FROM users")
        current_usernames = []
        for current_user in current_users:
            current_usernames.append(current_user["username"])

        if len(username) == 0:
            return render_template("apology.html", placeholder="Username must be provided")
        elif username in current_usernames:
            return render_template("apology.html", placeholder="Username already exists")

        if len(password) == 0:
            return render_template("apology.html", placeholder="Password must be provided")
        elif password != pw_confirmation:
            return render_template("apology.html", placeholder="Password did not match confirmation")

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/share_view", methods=["POST"])
@login_required
def share_view():
    """Get the view in database"""

    movie_title = request.form.get("movie-title")
    # Check movie title
    try:
        response = lookup(movie_title, "title")
    except:
        return render_template("apology.html", placeholder="HTTPError: 404 Client Error: NOT FOUND")

    response = loads(response)

    if response["Response"] == "False":
        return render_template("apology.html", placeholder="Movie title not found")

    view = request.form.get("view")
    # Check if view is empty
    if view == "":
        return render_template("apology.html", placeholder="You did not give your view")

    # Max character: 500
    if len(view) > 500:
        return render_template("apology.html", placeholder="Max character: 500")

    # Determine current date and time
    now = datetime.datetime.now()
    date = now.strftime("%D")
    time = now.strftime("%T")

    # Add view into database
    db.execute("INSERT INTO views (user_id, view, imdb_id, date, time) VALUES(?, ?, ?, ?, ?)", session["user_id"], view, response["imdbID"], date, time)

    return redirect("/")


@app.route("/myprofile")
@login_required
def myprofile():
    """Display user's profile"""
    views = db.execute("SELECT * FROM views INNER JOIN users ON views.user_id = users.id WHERE user_id = ? ORDER BY date DESC, time DESC", session["user_id"])

    # Get views info into a list
    views_movie_info = []
    for view in views:
        try:
            info_str = lookup(view["imdb_id"], "id")
            info = loads(info_str)
            views_movie_info.append(info)
        except:
            views_movie_info.append(None)

    # Get user infos
    users = db.execute("SELECT * FROM users")


    return render_template("myprofile.html", users=users, views=views, info=views_movie_info, length=len(views))
