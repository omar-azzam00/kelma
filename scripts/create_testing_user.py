import sys
sys.path.append("D:\\dev\\projects\\kelma")

from app import create_app
from app.tests.helpers import create_user

app = create_app()
with app.app_context():
    create_user("testing", "testing@gmail.com", "password")