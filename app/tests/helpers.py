from app import db
from hashlib import sha256
from app.models import User, Kelma
from random import randint
import random
from flask import current_app
import os
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

USED_REDIRECT_CODES = [302]


def create_user(
    username="default", email="default@gmail.com", plain_password="password"
):
    """This creates a user in the db and returns him\n\n
    it expects an app_context to be present"""
    hash = sha256(plain_password.encode("utf-8")).hexdigest()
    user = User(username=username, email=email, password=hash)
    db.session.add(user)
    db.session.commit()
    return user


def get_user(**kwargs):
    """This gets a user from the db and returns him using a syntax like sqlalchemy filter_by\n\n
    it expects an app_context to be present"""
    return db.session.execute(db.select(User).filter_by(**kwargs)).scalar_one()


def create_random_kelmas(n, sort_start=1, user_pattern="default_", premium=False):
    """It creates random n users and random n kelmas in db\n
    note that the sort increase sequentially.\n
    if premium is true so reserved end is filled with dates that has time delta of 1, 3 or 6 months.\n
    it expects an app_context to be available"""

    for i in range(n):
        user = create_user(
            f"{user_pattern}{i}", f"{user_pattern}{i}@gmail.com", "password"
        )
        db.session.add(user)
    db.session.commit()

    for i in range(n):
        reserve_end = None
        if premium:
            RESERVE_LENGTH = random.choice([1, 3, 6])
            now = datetime.now() + timedelta(days=30 * int(RESERVE_LENGTH))
            reserve_end = now.replace(
                microsecond=0, second=0, hour=0, minute=0
            ) + timedelta(days=1)
        kelma = Kelma(
            image_fn=f"profile_{i}.jpg",
            display_name="arbitrary display name Name",
            username=f"{user_pattern}{i}",
            content="arbitrary content",
            sort=sort_start + i,
            reserve_end=reserve_end
        )
        db.session.add(kelma)
    db.session.commit()


def get_n_kelmas(n=-1):
    """Get n kelmas from the database ordered by id, if n = -1 then get all kelmas\n\n
    it expects an app_context to be available"""

    if n < 0:
        return db.session.execute(db.select(Kelma).order_by(Kelma.id)).scalars().all()
    return (
        db.session.execute(db.select(Kelma).order_by(Kelma.id).limit(n)).scalars().all()
    )


def get_kelma(**kwargs):
    """This gets a kelma from the db and returns him using a syntax like sqlalchemy filter_by\n\n
    it expects an app_context to be present"""
    return db.session.execute(db.select(Kelma).filter_by(**kwargs)).scalar_one()


def get_kelma_image_path(image_fn):
    if current_app.static_folder == None:
        raise "Static Folder is None!"
    return os.path.join(
        current_app.static_folder, current_app.config["PROFILE_IMGS_PATH_OS"], image_fn
    )

def selenium_log_in(driver, username_or_email, password):
        driver.get("http://127.0.0.1:5000/login")
        
        wait = WebDriverWait(driver, timeout=2)
        wait.until(
            lambda _: len(driver.find_elements(By.TAG_NAME, 'input')) != 0
        )
        inputFields = driver.find_elements(By.TAG_NAME, 'input')
        
        for inputField in inputFields:
            if inputField.get_attribute('type') == 'text':
                inputField.send_keys(username_or_email)
            elif inputField.get_attribute('type') == 'password':
                inputField.send_keys(password)
            elif inputField.get_attribute('type') == 'submit':
                inputField.click()
                break