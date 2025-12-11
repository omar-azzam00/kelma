from flask import redirect, url_for, session, g, current_app
from app import db
from app.exceptions import NoUserInDb, NoUserInSession
from app.models import User
from hashlib import sha256
from typing import Callable
from functools import wraps
import string
import secrets

def login_user(user_id: int, permanent: bool) -> None:
    """sets both the user_id and permanent option in the session.\n\n
    
    raises a TypeError exception if user_id is not an int or permanent
    is not a bool. 
    """
    
    if not isinstance(user_id, int):
        raise TypeError("user_id is expected to be int")
    elif not isinstance(permanent, bool):
        raise TypeError("permanent is expected to be bool")

    session["user_id"] = user_id
    session.permanent = permanent


def logged_in() -> bool:
    """Checks if the session contains an existent user_id."""
    
    try: 
        get_user()
    except (NoUserInSession, NoUserInDb):
        return False
    return True

def get_user() -> User | None:
    """Gets the user specified by the user_id in the session.\n
    if there is no user_id in the session it raises NoUserInSession, 
    also if the user is not found in the db it raises NoUserInDb.
    """
    
    user_id = session.get("user_id")
    if not user_id:
        raise NoUserInSession()

    user = db.session.execute(
        db.select(User).filter_by(id=user_id)
    ).scalar_one_or_none()
    if not user:
        raise NoUserInDb()

    return user

def generate_hash(plain: str) -> str:
    """Returns the SHA-256 of the plain parameter as hex string."""

    hash_obj = sha256()
    hash_obj.update(plain.encode("utf-8"))
    return hash_obj.hexdigest()

def login_required(view: Callable) -> Callable:
    """This function can be used as a decorator on any endpoint,
    if the user is logged in a user object is available via g.user,
    otherwise the user is redirected to the login endpoint"""
    
    @wraps(view)
    def decorated_view(*args, **kwargs):
        try:
            g.user = get_user()
        except (NoUserInSession, NoUserInDb):
            return redirect(url_for(current_app.config['LOGIN_ENDPOINT']))    
        return view(*args, **kwargs)
    return decorated_view

ALPHANUMERIC = string.ascii_letters + string.digits
def generate_password_reset_token() -> str:
    """A password reset token is 12 random characters from alphanumeric charset"""
    
    LENGTH = 12
    
    return ''.join([secrets.choice(ALPHANUMERIC) for _ in range(LENGTH)])