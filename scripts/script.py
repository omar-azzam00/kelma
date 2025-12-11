import sys

sys.path.append("D:\\dev\\projects\\kelma")

from app import create_app, db
from app.tests.helpers import create_user
from app.models import Kelma
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    user = create_user("hello", "hello@gmail.com")
    kelma = Kelma(
        username=user.username,
        display_name="",
        content="",
        sort=1,
        reserve_end=datetime.now() - timedelta(days=1),
    )
    db.session.add(kelma)
    db.session.commit()
