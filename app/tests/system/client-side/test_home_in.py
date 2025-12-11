from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from app import db
from app.models import Kelma
import app.tests.helpers as helpers
import json
import datetime
from threading import Thread
from time import sleep

def test_all_kelmas_are_displayed_and_unique(app):
    # you should be running an app that is using test config before this test
    
    USERNAME = "testing"
    EMAIL = "testing@gmail.com"
    PASSWORD = "password"

    PREMIUM_N = 20
    NORMAL_N = 200
    ALL_N = PREMIUM_N + NORMAL_N
    
    ctx = app.test_request_context()
    ctx.push()
        
    user = helpers.create_user(USERNAME, EMAIL, PASSWORD)
    helpers.create_random_kelmas(PREMIUM_N, 1, "premium", True)
    top_kelmas = (
        db.session.execute(db.select(Kelma).where(Kelma.reserve_end != None))
        .scalars()
        .all()
    )
    helpers.create_random_kelmas(NORMAL_N, 21, "normal")
    all_kelmas = db.session.execute(db.select(Kelma)).scalars().all()
    driver = webdriver.Firefox()
    helpers.selenium_log_in(driver, USERNAME, PASSWORD)
    assert driver.current_url == "http://127.0.0.1:5000/"

    top_kelmas_container = driver.find_element(By.ID, "topKelmasContainer")
    wait = WebDriverWait(driver, timeout=2)
    wait.until(
        lambda _: len(top_kelmas_container.find_elements(By.XPATH, "./div")) == 20
    )
    top_kelmas_elems = top_kelmas_container.find_elements(By.XPATH, "./div")

    assert len(top_kelmas_elems) == 20
    for i in range(20):
        kelma_elem = top_kelmas_elems[i]
        user_kelma_dict = json.loads(kelma_elem.get_attribute("x-data"))[
            "kelma"
        ]
        server_kelma_dict = top_kelmas[i]._to_json()

        assert user_kelma_dict["sort"] == i + 1
        assert user_kelma_dict['sort'] == server_kelma_dict['sort']
        assert user_kelma_dict['id'] == server_kelma_dict['id']

    all_kelmas_container = driver.find_element(By.ID, "allKelmasContainer")
    show_more_btn = driver.find_element(By.ID, "showMoreBtn")

    while True:
        try:
            wait = WebDriverWait(driver, timeout=2)
            wait.until(lambda _: show_more_btn.is_displayed())
        except:
            print("Timeout encountered!")
            break
        sleep(.1)
        while True:
            driver.execute_script('window.scrollTo(0, document.body.offsetHeight)')
            try:
                show_more_btn.click()
                break
            except ElementClickInterceptedException:
                pass
        
    all_kelmas_elems = all_kelmas_container.find_elements(By.XPATH, "./div")

    assert len(all_kelmas_elems) == ALL_N

    id_set = set()
    for i in range(ALL_N):
        kelma_elem = all_kelmas_elems[i]
        user_kelma_dict = json.loads(kelma_elem.get_attribute("x-data"))[
            "kelma"
        ]
        server_kelma_dict = all_kelmas[i]._to_json()
        
        assert user_kelma_dict['id'] not in id_set
        assert user_kelma_dict["sort"] == i + 1
        assert user_kelma_dict['sort'] == server_kelma_dict['sort']
        assert user_kelma_dict['id'] == server_kelma_dict['id']
        
        id_set.add(user_kelma_dict['id'])
    
    ctx.pop()
    driver.close()