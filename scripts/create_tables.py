import sys
sys.path.append("D:\\dev\\projects\\kelma")

from app import create_app, db
from app.models import *


app = create_app()
with app.app_context():
    if 'y' == input("Do you want to drop the tables [y/N]? ").strip().lower():
        db.drop_all()
    db.create_all()
