import app.tests.helpers as helpers
import bs4

def test_login_get_is_working(client):
    resp = client.get("/login")
    assert resp.status_code >= 200 and resp.status_code < 300

def test_login_post_with_valid_username_and_password(app, client):
    username = "t"*50
    password = "s"*255

    with app.app_context():
        helpers.create_user(username, "anything@gmail.com", password)

    # get csrf token
    resp = client.get("/login")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']

    data = {"username_or_email": username, "password": password, "csrf_token": csrf_token}
    resp = client.post("/login", data=data)

    # a redirect means login was successful
    assert resp.status_code >= 300 and resp.status_code < 400

def test_login_post_with_valid_email_and_password(app, client):
    email = "a"*(254-10) + "@gmail.com"
    password = "securepassword"

    with app.app_context():
        helpers.create_user("anything", email, password)

    # get csrf token
    resp = client.get("/login")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']

    data = {"username_or_email": email, "password": password, "csrf_token": csrf_token}
    resp = client.post("/login", data=data)

    # a redirect means login was successful
    assert resp.status_code >= 300 and resp.status_code < 400

def test_login_without_csrf_token(app, client):
    username = "testuser"
    email = "testemail@gmail.com"
    password = "securepassword"
    
    with app.app_context():
        helpers.create_user(username, email, password)

    data = {"username_or_email": username, "password": password}
    resp = client.post("/login", data=data)

    assert resp.status_code == 400

def test_login_with_non_existent_username(app, client):
    username = "nonexistent"
    password = "securepassword"

    # get csrf token
    resp = client.get("/login")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']

    data = {"username_or_email": username, "password": password, "csrf_token": csrf_token}
    resp = client.post("/login", data=data)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    # should return page with errors
    assert resp.status_code == 200


def test_login_with_non_existent_email(app, client):
    email = "nonexistent@gmail.com"
    password = "securepassword"

    # get csrf token
    resp = client.get("/login")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']

    data = {"username_or_email": email, "password": password, "csrf_token": csrf_token}
    resp = client.post("/login", data=data)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    # should return page with errors
    assert resp.status_code == 200

def test_login_with_username_and_invalid_password(app, client):
    username = "testuser"
    password = "securepassword"
    wrong_password = "wrongpassword"

    with app.app_context():
        helpers.create_user(username=username, email="anything@gmail.com", plain_password=password)

    # get csrf token
    resp = client.get("/login")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']

    data = {"username_or_email": username, "password": wrong_password, "csrf_token": csrf_token}
    resp = client.post("/login", data=data)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    # should return page with errors
    assert resp.status_code == 200

def test_login_with_email_and_invalid_password(app, client):
    email = "email@gmail.com"
    password = "securepassword"
    wrong_password = "wrongpassword"

    with app.app_context():
        helpers.create_user(username="anything", email=email, plain_password=password)

    # get csrf token
    resp = client.get("/login")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"type":"hidden"}).attrs['value']

    data = {"username_or_email": email, "password": wrong_password, "csrf_token": csrf_token}
    resp = client.post("/login", data=data)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    # should return page with errors
    assert resp.status_code == 200