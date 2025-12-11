from app.utils import auth
from hashlib import sha256
from flask import request, session, url_for, g
import pytest
from app import db, exceptions
from flask import Blueprint
import app.tests.helpers as helpers
import flask

# refer to flask testing docs to know how to use app and client fixtures
def test_generate_hash_with_normal_string():
    plain = "helloworld"
    
    assert auth.generate_hash(plain) == sha256(plain.encode()).hexdigest()    

def test_generate_hash_with_empty_string():
    plain = ""
    
    assert auth.generate_hash(plain) == sha256(plain.encode()).hexdigest()   

def test_generate_hash_with_invalid_type():
    plain = 5
    
    with pytest.raises(Exception):
        auth.generate_hash(plain)              

def test_login_user_with_normal_input(app):
    user_id = 100
    permanent = True
    
    with app.test_request_context():
        auth.login_user(user_id, permanent)
        assert session['user_id'] == user_id
        assert session.permanent

def test_login_user_preserve_the_rest_of_the_session(app):
    user_id = 100
    permanent = True
    session_field = "test"
    
    with app.test_request_context():
        session['session_field'] = session_field
        auth.login_user(user_id, permanent)
        
        assert session.get('session_field') == session_field
        assert session['user_id'] == user_id
        assert session.permanent

def test_login_user_with_invalid_user_id(app):
    user_id = "name"
    permanent = True
    
    with app.test_request_context():
        with pytest.raises(TypeError):
            auth.login_user(user_id, permanent)

def test_login_user_with_invalid_permanent(app):
    user_id = 10
    permanent = "str"
    
    with app.test_request_context():
        with pytest.raises(TypeError):
            auth.login_user(user_id, permanent)
    
def test_logged_in_returns_true(app):
    user_id = 10
    with app.test_request_context():
        user = helpers.create_user(app)
        session['user_id'] = user.id
        assert auth.logged_in()

def test_logged_in_returns_false(app):
    with app.test_request_context():
        assert not auth.logged_in()

def test_logged_in_returns_false_2(app):
    user_id = 10
    with app.test_request_context():
        session['user_id'] = user_id
        assert not auth.logged_in()

def test_get_user_returns_obj(app):
    with app.test_request_context():
        user = helpers.create_user(app)
        session['user_id'] = user.id
        assert user == auth.get_user()

def test_get_user_with_no_user_id_in_session(app):
    with app.test_request_context():
        with pytest.raises(exceptions.NoUserInSession):
            auth.get_user()

def test_get_user_with_no_user_in_db(app):
    with app.test_request_context():
        # a value that has no corresponding user.
        session['user_id'] = 999
        with pytest.raises(exceptions.NoUserInDb):
            assert auth.get_user() == None

def test_login_required_with_logged_out_user(app, client):
    login_endpoint = "auth.login"
    
    @app.route("/testing_route")
    @auth.login_required
    def testing():
        return str(g.user)   
     
    with client:        
        resp = client.get("/testing_route")
        assert resp.status_code in helpers.USED_REDIRECT_CODES
        assert resp.headers['Location'] == url_for(login_endpoint) 
        with pytest.raises(AttributeError):
            g.user

def test_login_required_with_not_found_user(app, client):
    login_endpoint = "auth.login"
    
    @app.route("/testing_route")
    @auth.login_required
    def testing():
        return str(g.user)   
     
    with client:
        with client.session_transaction() as session:
            # any random id that doesn't exist
            session['user_id'] = 999
        resp = client.get("/testing_route")
        assert resp.status_code in helpers.USED_REDIRECT_CODES
        assert resp.headers['Location'] == url_for(login_endpoint) 
        with pytest.raises(AttributeError):
            g.user

def test_login_required_with_logged_in_user(app, client):
    login_endpoint = "auth.login"
    
    @app.route("/testing_route")
    @auth.login_required
    def testing():
        return str(g.user)
    
    with app.app_context():        
        user = helpers.create_user()  
        # this client will create a request context but as an app_context is already present 
        # so it will use it instead of creating a new one.
        with client: 
            with client.session_transaction() as session:
                session['user_id'] = user.id
            resp = client.get("/testing_route")

            assert resp.status_code >= 200 and resp.status_code < 300
            assert resp.text == str(g.user) == str(user)
            assert g.user == user

def test_login_required_with_different_users(app, client):
    login_endpoint = "auth.login"
    
    @app.route("/testing_route")
    @auth.login_required
    def testing():
        return str(g.user)
    
    with app.app_context():        
        user = helpers.create_user()  
        # this client will create a request context but as an app_context is already present 
        # so it will use it instead of creating a new one.
        with client: 
            with client.session_transaction() as session:
                session['user_id'] = user.id
            resp = client.get("/testing_route")

            assert resp.status_code >= 200 and resp.status_code < 300
            assert resp.text == str(g.user) == str(user)
            assert g.user == user
    
    with client:  
        with client.session_transaction() as session:
            session.clear()      
        resp = client.get("/testing_route")
        assert resp.status_code in helpers.USED_REDIRECT_CODES
        assert resp.headers['Location'] == url_for(login_endpoint) 
        with pytest.raises(AttributeError):
            g.user    
    
    with app.app_context():        
        user = helpers.create_user("default2", "default2@gmail.com")  
        # this client will create a request context but as an app_context is already present 
        # so it will use it instead of creating a new one.
        with client: 
            with client.session_transaction() as session:
                session['user_id'] = user.id
            resp = client.get("/testing_route")

            assert resp.status_code >= 200 and resp.status_code < 300
            assert resp.text == str(g.user) == str(user)
            assert g.user == user
        