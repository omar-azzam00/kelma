import os
from datetime import timedelta
from app.secrets import DATABASE_URI, TESTING_DATABASE_URI, MAIL_USERNAME, MAIL_PASSWORD

class Dev_Config:
    def __init__(self):
        self.PROFILE_IMGS_PATH_OS = os.path.join(*self.PROFILE_IMGS_PATH)
        self.PROFILE_IMGS_PATH_URL = '/'.join(self.PROFILE_IMGS_PATH)

    SECRET_KEY = "REDACTED"
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_ECHO = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=181)  
    # the path inside the static folder.
    PROFILE_IMGS_PATH = ['images', 'kelmas_images']
    LOGIN_ENDPOINT = 'auth.login'
    PRICE_FOR_MONTH = 200
    PREMIUM_COUNT = 20
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587 
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = MAIL_USERNAME + "@gmail.com"
class Test_Config(Dev_Config):
    def __init__(self):
        super().__init__()

    TESTING = True
    SQLALCHEMY_DATABASE_URI = TESTING_DATABASE_URI
    SQLALCHEMY_ECHO = False
    PROFILE_IMGS_PATH = ['images', 'testing_kelmas_images']
    
