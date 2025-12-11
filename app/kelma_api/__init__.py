from flask import Blueprint

kelma_api = Blueprint("kelma_api", __name__)

from app.kelma_api.routes import *