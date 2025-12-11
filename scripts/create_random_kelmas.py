import sys
sys.path.append("D:\\dev\\projects\\kelma")

from app import create_app, db
from app.tests.helpers import create_random_kelmas, create_user
from app.models import Kelma
from app.utils.main import get_random_sort

app = create_app()
with app.app_context():
    PREMIUM_COUNT = 20
    NORMAL_COUNT = 100
    create_random_kelmas(NORMAL_COUNT, PREMIUM_COUNT + 1, 'normal')
    create_random_kelmas(PREMIUM_COUNT, 1, 'premium', premium=True)
    
    # create_random_kelmas(100, 21)
   