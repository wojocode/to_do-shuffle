import re
from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


#PASSWORD VALIDATOR
def validate_password(password):
# at least 8 characters
    pattern = r"^(?=.*[a-zA-Z0-9]{8,})"
    if re.match(pattern, password):
        return True
    else:
        return False