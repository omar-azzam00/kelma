import pytest
from app import create_app, db
from flask import current_app
from app.models import User
from hashlib import sha256
import app.tests.test_models
import os
        
@pytest.fixture()
def app():
    app = create_app("test")
    
    destruct(app)    
    set_up(app)
    
    yield app  

@pytest.fixture()
def client(app):
    return app.test_client()

def set_up(app):
    with app.app_context():
        db.create_all()
        
def destruct(app):
    with app.app_context():
        db.drop_all()
    
    # if app.static_folder == None:    
    #     raise "Static Folder is None!"  
    # dir = os.path.join(app.static_folder, app.config['PROFILE_IMGS_PATH'])
    # if os.path.exists(dir):
    #     for file in os.listdir(dir):
    #         os.remove(os.path.join(dir, file))
    #     os.rmdir(dir)