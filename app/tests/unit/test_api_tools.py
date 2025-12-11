from app.utils.api_tools import ultra_serialize
import json
from datetime import datetime
import pytest
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
import app.tests.helpers as helpers
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.tests.test_models import Person
from sqlalchemy import text

def test_ultra_serialize_with_to_json():
    class Person:
        def __init__(self):
            self.name = 'ahmed'
            self.age = 18
        def _to_json(self):
            return {'name': self.name}
        def to_dict(self):
            return {'name': self.name, 'age': self.age}
    obj = Person()
    
    serialized = json.dumps(obj, default=ultra_serialize)
    assert obj._to_json() == json.loads(serialized)
    


def test_ultra_serialize_with_datetime():
    now = datetime.now()
    serialized = json.dumps(now, default=ultra_serialize)
    assert str(now) == json.loads(serialized)

def test_ultra_serialize_raises():
    class Person:
        def __init__(self):
            self.name = 'ahmed'
            self.age = 18
    obj = Person()
    
    with pytest.raises(Exception):
        json.dumps(obj) 


def test_ultra_serialize_with_row(app):
    with app.app_context():
        p = Person(name="ahmed")
        db.session.add(p)
        db.session.commit()
        persons = db.session.execute(db.select(Person.name)).all()
        serialized = json.dumps(persons, default=ultra_serialize)
        assert json.loads(serialized) == [{'name': p.name}]
        
