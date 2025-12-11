import app.tests.helpers as helpers
from flask import url_for
import bs4
import os
from datetime import datetime, timedelta
from app.models import Kelma
from app import db

TESTING_IMAGE = "D:\\dev\\projects\\kelma\\app\\tests\\test.png"


def test_get_while_not_logged_in(app, client):
    with app.app_context():
        resp = client.get("/kelma")
        assert resp.status_code in helpers.USED_REDIRECT_CODES


def test_post_while_not_logged_in(app, client):
    with app.app_context():
        resp = client.get("/kelma")
        assert resp.status_code in helpers.USED_REDIRECT_CODES


def test_get_while_logged_in(app, client):
    with app.app_context():
        user = helpers.create_user()
        with client.session_transaction() as session:
            session["user_id"] = user.id
        resp = client.get("/kelma")
        assert resp.status_code >= 200 and resp.status_code <= 300
        assert resp.status_code not in helpers.USED_REDIRECT_CODES


def test_post_with_no_csrf(app, client):
    with app.app_context():
        user = helpers.create_user()
        with client.session_transaction() as session:
            session["user_id"] = user.id
        resp = client.post("/kelma")
        assert resp.status_code == 400


def test_post_with_no_data(app, client):
    with app.app_context():
        user = helpers.create_user()
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post("/kelma", data={"csrf_token": csrf_token})
        # since there is no redirect this means that the submitting failed.
        assert resp.status_code >= 200 and resp.status_code <= 300
        assert resp.status_code not in helpers.USED_REDIRECT_CODES


def test_post_with_valid_data(app, client):
    with app.app_context():
        user = helpers.create_user()
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": "testing",
                "kelma_type": "top_twenty",
                "reserve_length": "6",
                "content": "testing",
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES


def test_empty_kelmas_with_normal(app, client):
    KELMA_TYPE = "normal"
    RESERVE_LENGTH = "6"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    with app.app_context():
        user = helpers.create_user()
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username
        assert kelma.reserve_end == None
        assert kelma.sort == 1
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))


def test_empty_kelmas_with_premium(app, client):
    KELMA_TYPE = "top_twenty"
    RESERVE_LENGTH = "1"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    with app.app_context():
        user = helpers.create_user()
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username

        now = datetime.now() + timedelta(days=30 * int(RESERVE_LENGTH))
        # reserve_end = now.replace(
        #     microsecond=0, second=0, hour=0, minute=0
        # ) + timedelta(days=1)
        # assert kelma.reserve_end == reserve_end
        # assert kelma.sort == 1
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))


def test_full_kelmas_with_normal(app, client):
    KELMA_TYPE = "normal"
    RESERVE_LENGTH = "6"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 1)
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username
        assert kelma.reserve_end == None
        assert kelma.sort >= 21
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))


def test_full_kelmas_with_premium(app, client):
    KELMA_TYPE = "top_twenty"
    RESERVE_LENGTH = "1"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 21)
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username

        now = datetime.now() + timedelta(days=30 * int(RESERVE_LENGTH))
        # reserve_end = now.replace(
        #     microsecond=0, second=0, hour=0, minute=0
        # ) + timedelta(days=1)
        # assert kelma.reserve_end == reserve_end
        # assert kelma.sort == 1
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))


def test_full_kelmas_some_premium_with_normal(app, client):
    KELMA_TYPE = "normal"
    RESERVE_LENGTH = "6"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    PREMIUM_COUNT = 10
    PREMIUM_START = 1
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 21)
        helpers.create_random_kelmas(
            PREMIUM_COUNT, PREMIUM_START, "default_2_", premium=True
        )
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username
        assert kelma.reserve_end == None
        assert kelma.sort >  PREMIUM_COUNT
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))

def test_full_kelmas_some_premium_with_normal(app, client):
    KELMA_TYPE = "normal"
    RESERVE_LENGTH = "6"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    PREMIUM_COUNT = 10
    PREMIUM_START = 1
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 21)
        helpers.create_random_kelmas(
            PREMIUM_COUNT, PREMIUM_START, "default_2_", premium=True
        )
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        
        seen_sort = set()
        sorts = db.session.execute(db.select(Kelma.sort)).scalars().all()
        kelma = helpers.get_kelma(username=user.username)
        for sort in sorts:
            assert sort not in seen_sort
            seen_sort.add(sort)
                
        

def test_full_kelmas_some_premium_with_premium(app, client):
    KELMA_TYPE = "top_twenty"
    RESERVE_LENGTH = "1"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    PREMIUM_COUNT = 10
    PREMIUM_START = 1
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 21)
        helpers.create_random_kelmas(
            PREMIUM_COUNT, PREMIUM_START, "default_2_", premium=True
        )

        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username

        # now = datetime.now() + timedelta(days=30 * int(RESERVE_LENGTH))
        # reserve_end = now.replace(
        #     microsecond=0, second=0, hour=0, minute=0
        # ) + timedelta(days=1)
        # assert kelma.reserve_end == reserve_end
        # assert kelma.sort == PREMIUM_START + PREMIUM_COUNT
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))


def test_full_kelmas_full_premium_with_normal(app, client):
    KELMA_TYPE = "normal"
    RESERVE_LENGTH = "6"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    PREMIUM_COUNT = 20
    PREMIUM_START = 1
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 21)
        helpers.create_random_kelmas(
            PREMIUM_COUNT, PREMIUM_START, "default_2_", premium=True
        )
        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]
        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        assert resp.status_code in helpers.USED_REDIRECT_CODES

        kelma = helpers.get_kelma(username=user.username)
        assert kelma.display_name == DISPLAY_NAME
        assert kelma.content == CONTENT
        assert kelma.username == user.username
        assert kelma.reserve_end == None
        assert kelma.sort >= 21
        assert kelma.image_fn.endswith(".png")
        assert os.path.exists(helpers.get_kelma_image_path(kelma.image_fn))


def test_full_kelmas_full_premium_with_premium(app, client):
    KELMA_TYPE = "top_twenty"
    RESERVE_LENGTH = "1"
    DISPLAY_NAME = "testing"
    CONTENT = "testing"

    PREMIUM_COUNT = 20
    PREMIUM_START = 1
    with app.app_context():
        user = helpers.create_user()
        helpers.create_random_kelmas(100, 21)
        helpers.create_random_kelmas(
            PREMIUM_COUNT, PREMIUM_START, "default_2_", premium=True
        )

        with client.session_transaction() as session:
            session["user_id"] = user.id
        # get csrf token
        resp = client.get("/kelma")
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden"}).attrs["value"]

        resp = client.post(
            "/kelma",
            data={
                "display_name": DISPLAY_NAME,
                "kelma_type": KELMA_TYPE,
                "reserve_length": RESERVE_LENGTH,
                "content": CONTENT,
                "image": (TESTING_IMAGE,),
                "csrf_token": csrf_token,
            },
        )
        # this should return an error as creating a kelma with full kelmas should do this.
        assert resp.status_code == 200
