import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(input, method):
    API_key = "94819a2"
    if method == "title":
        response = requests.get(f"http://www.omdbapi.com/?t={input}&apikey={API_key}")
    elif method == "id":
        response = requests.get(f"http://www.omdbapi.com/?i={input}&apikey={API_key}")

    response.raise_for_status()

    return response.text

