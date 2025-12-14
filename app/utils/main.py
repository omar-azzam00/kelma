import os
from flask import current_app
from PIL import Image
import os
from secrets import token_hex
from app.models import Kelma
from random import randint
from app import db
from datetime import datetime, timedelta, date
from sqlalchemy import func, case, text
from PIL import ImageOps
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


def extend_kelma_reserve_end(kelma: Kelma, months: int):
    """if reserve_end is none then it will be calculated from today."""

    if kelma.reserve_end == None:
        today = date.today()
        kelma.reserve_end = today + timedelta(days=30 * months)
    else:
        kelma.reserve_end = kelma.reserve_end + timedelta(days=months * 30)


def save_thumbnail(uploaded_image, fn=None):
    """saves a version of the provided image file that has {SIZE} dimensions to {static_folder_path}/{profile_imgs_path}
    as a png with a random name and returns that name,\n
    it raises an exception if anything in the process failed."""

    SIZE = (256, 256)

    im = Image.open(uploaded_image)
    if fn == None:
        _, ext = os.path.splitext(uploaded_image.filename)
        fn = f"{token_hex(12)}{ext}"

    folder_path = os.path.join(
        current_app.static_folder, current_app.config["PROFILE_IMGS_PATH_OS"]
    )
    os.makedirs(folder_path, exist_ok=True)
    f_path = os.path.join(folder_path, fn)

    im = ImageOps.fit(im, SIZE)
    im.save(f_path)
    return fn


def get_all_count():
    """Returns the current count of all kelmas"""

    return db.session.execute(
        db.select(func.count()).select_from(Kelma).where(Kelma.sort != None)
    ).scalar_one()


def get_premium_count():
    """Returns the current count of premium kelmas"""

    return db.session.execute(
        db.select(func.count())
        .select_from(Kelma)
        .where(Kelma.sort != None, Kelma.reserve_end != None)
    ).scalar_one()


def get_first_available_date():
    """Returns the the minimum reserve_end date for premium."""

    return db.session.execute(
        db.select(func.min(Kelma.reserve_end)).where(Kelma.sort != None)
    ).scalar_one()


def get_info() -> tuple:
    """It returns the tuple (premium_count, first_available_date)"""

    return db.session.execute(
        db.select(
            func.count(
                case(
                    (Kelma.reserve_end != None, 1),
                    else_=None,
                )
            ).label("premium_count"),
            func.min(Kelma.reserve_end).label("first_available_date"),
        )
    ).one()


def get_random_sort(all_count=None):
    """Gets a random sort that is not in the top 20,
    unless top 20 is not full in this case it just
    returns the next sort"""

    if all_count == None:
        all_count = get_all_count()

    if all_count <= 20:
        return all_count + 1
    else:
        return randint(21, all_count + 1)


def ceil_datetime(dt):
    """It ceils a datetime to the next day."""

    return dt.replace(microsecond=0, second=0, hour=0, minute=0) + timedelta(days=1)


def shift_sort_from(sort: int):
    """It adds 1 to the sort of all kelmas.sort >= {sort}"""
    
    stmt = text(
        """
                UPDATE kelma 
                SET sort = sort + 1 
                WHERE sort is NOT NULL AND sort >= :sort
                ORDER BY sort DESC
        """
    )

    # db.session.execute(
    #     db.update(Kelma)
    #     .where(Kelma.sort != None, Kelma.sort >= sort)
    #     .order_by(
    #         Kelma.sort.desc(),
    #     )
    #     .values(sort=Kelma.sort + 1)
    # )

    db.session.execute(stmt, {"sort": sort})


def shift_sort_back_after(sort: int):
    """It subtracts 1 from the sort of all kelmas.sort > {sort}"""
    
    stmt = text(
        """
                UPDATE kelma 
                SET sort = sort - 1 
                WHERE sort is NOT NULL AND sort > :sort
                ORDER BY sort
        """
    )
    
    # db.session.execute(
    #     db.update(Kelma)
    #     .where(Kelma.sort != None, Kelma.sort > sort)
    #     .order_by(Kelma.sort)
    #     .values(sort=Kelma.sort - 1)
    # )
    
    db.session.execute(stmt, {"sort": sort})
    


def update_kelma_image(kelma, file) -> bool:
    """It saves the new image, update the kelma data and deletes the old image if it exists.
    returns True on success or False on failure"""

    if file is None:
        return True

    old_image_path = kelma.image_path
    try:
        kelma.image_fn = save_thumbnail(file)
    except:
        # TODO: Log as error
        return False
    if old_image_path is not None and os.path.exists(old_image_path):
        os.remove(old_image_path)
    return True


def delete_kelma(kelma):
    if kelma is None:
        return

    db.session.delete(kelma)
    db.session.flush()
    
    if kelma.sort is not None:
        shift_sort_back_after(kelma.sort)
