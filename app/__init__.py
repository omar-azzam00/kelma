from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from app.config import Dev_Config, Test_Config
from app.utils.filters import add_if_errors, readable_date, remaining_days_ceil
from sqlalchemy.orm import DeclarativeBase
from app.utils.api_tools import UltraJSONProvider
from flask_mail import Mail

# TODO: Foreign Keys should only reference primary keys on other tables 
# TODO: we should use logging through all the app so we can track what is happening
# TODO: we should use whatsapp or email notifications for situations which might require something like this
# TODO: we should create an admin web page or admin command line application so we can handle errors and manually change app data if needed.

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
mail = Mail()

def create_app(config_str="dev"):
    if config_str == "dev":
        config = Dev_Config()
    elif config_str == "test":
        config = Test_Config()
    else:
        raise Exception(f"Unknown config str '{config_str}'")

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    from app.auth import auth

    app.register_blueprint(auth)
    from app.main import main

    app.register_blueprint(main)
    from app.kelma_api import kelma_api

    app.register_blueprint(kelma_api)

    app.jinja_env.filters["add_if_errors"] = add_if_errors
    app.jinja_env.filters["readable_date"] = readable_date
    app.jinja_env.filters["remaining_days_ceil"] = remaining_days_ceil
    
    app.json = UltraJSONProvider(app)
    
    return app
