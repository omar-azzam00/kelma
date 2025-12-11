import app.tests.helpers as helpers 
from flask import url_for
import bs4
from hashlib import sha256

def test_register_get_is_working(client):
    resp = client.get("/register")
    assert resp.status_code >= 200 and resp.status_code < 300
    

def test_register_post_with_valid_form_data(app, client):
    username = "a"*50
    email = "a"*(255-11) + "@gmail.com"
    password = "p"*255
        
    # getting the csrf token
    resp = client.get("/register")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']
    
    data = {"username":username, "email":email, "password":password, "csrf_token":csrf_token}
    resp = client.post("/register", data=data)
    
    # a redirect means that the user is created successfully
    assert resp.status_code >= 300 and resp.status_code < 400
    
    with app.app_context():
        user = helpers.get_user(username=username)
        assert user.username == username
        assert user.email == email
        assert sha256(password.encode()).hexdigest() == user.password
        
def test_register_without_csrf_token(app, client):
    username = "default"
    email = "default@gmail.com"
    password = "password"
        
    data = {"username":username, "email":email, "password":password}
    resp = client.post("/register", data=data)
    
    assert resp.status_code == 400

def test_register_with_existing_username(app, client):
    username = "default"
    email = "default@gmail.com"
    password = "password"
    
    with app.app_context():
        user = helpers.create_user(username=username, email="different@gmail.com", plain_password=password)
        
        # getting the csrf token
        resp = client.get("/register")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']
        
        data = {"username":username, "email":email, "password":password, "csrf_token":csrf_token}
        resp = client.post("/register", data=data)
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        
        # this means that a page with errors has been returned
        assert resp.status_code == 200

def test_register_with_existing_email(app, client):
    username = "default"
    email = "default@gmail.com"
    password = "password"
    
    with app.app_context():
        user = helpers.create_user(username="different", email=email, plain_password=password)
        
        # getting the csrf token
        resp = client.get("/register")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']
        
        data = {"username":username, "email":email, "password":password, "csrf_token":csrf_token}
        resp = client.post("/register", data=data)
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        
        # this means that a page with errors has been returned
        assert resp.status_code == 200