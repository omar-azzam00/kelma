from app import db
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

class Person(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))