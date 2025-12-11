from app import db
from app.models import User
from wtforms import ValidationError
from wtforms.validators import InputRequired, Optional

from PIL import Image, UnidentifiedImageError


def UsernameUnique(message: str = "Username already exists!", exclude=[]):
    """A wtforms validator that makes sure an inputted username isn't used by any existent user in the db."""

    def _username_unique(form, field):
        user = db.session.execute(
            db.select(User).filter_by(username=field.data)
        ).scalar_one_or_none()
        if user and user.username not in exclude:
            raise ValidationError(message)

    return _username_unique


def EmailUnique(message: str = "Email already exists!", exclude=[]):
    """A wtforms validator that makes sure an inputted email isn't used by any existent user in the db."""

    def _email_unique(form, field):
        user = db.session.execute(
            db.select(User).filter_by(email=field.data)
        ).scalar_one_or_none()
        if user and user.email not in exclude:
            raise ValidationError(message)

    return _email_unique

def EmailExists(message: str = "هذا البريد الإلكتروني غير موجود!"):
    """A wtforms validator that makes sure an inputted email exists in the db."""

    def _email_exists(form, field):
        user = db.session.execute(
            db.select(User).filter_by(email=field.data)
        ).scalar_one_or_none()
        if user is None:
            raise ValidationError(message)

    return _email_exists

def RequiredIfField(other_field: str, value, message: str | None = None):
    """A wtforms validators that makes a field only required if another field in the form have a specific value."""

    required = InputRequired(message=message)
    optional = Optional()

    def _required_if(form, field):
        if getattr(form, other_field).data == value:
            required(form, field)
        else:
            optional(form, field)

    return _required_if