from app.kelma_api import kelma_api
from app.utils.api_tools import get_int_from_url, convert_to_id
from app import db
from app.models import Kelma
from sqlalchemy import select
from time import sleep
from flask import request, abort

# This is the old api route.
@kelma_api.route("/api/kelmas")
def get_kelmas():
    """api/kelmas?start={start}&size={size}&page={page}\n
    all parameters should be >= 0 otherwise a bad request (400) is returned\n
    it returns a json list of Kelma objects that has the following properties:\n
    sort: int, this represents it is unique sort between all other kelmas\n
    id: int\n
    created_at: string, format example: 2025-09-12 12:33:00\n
    image_url: string\n
    display_name: string\n
    username: string\n
    content: string\n
    premium: bool\n
    """
    start = get_int_from_url("start")
    size = get_int_from_url("size", default=1, min=0)
    page = get_int_from_url("page")
    result = get_kelmas_local(start, size, page)
    return result


def get_kelmas_local(start, size, page):    
    result = db.session.execute(
        db.select(Kelma)
        .where(
            Kelma.sort != None, Kelma.sort >= start + 1 + page * size, Kelma.sort < (start + 1 + page * size) + size
        )
        .order_by(Kelma.sort)
    ).scalars().all()
    return result


# TODO: NEW COMMUNICATION MODEL
"""
1- at any communication the server returns an id list with its last update date or a version indicator
2- the client can then request this easily with an id list if he doesn't have a specific updated kelma
"""
@kelma_api.route("/api/kelmas/range")
def kelmas_range():
    """api/kelmas?start={start}&size={size}&page={page}\n
    all parameters should be >= 0 otherwise a bad request (400) is returned\n
    it returns a json list of objects that has the following properties:\n
    id: int\n
    version: int\n
    """
    sleep(1)
    start = get_int_from_url("start")
    size = get_int_from_url("size", default=1, min=0)
    page = get_int_from_url("page")
    result = kelmas_range_local(start, size, page)
    return result


def kelmas_range_local(start, size, page):    
    result = db.session.execute(
        db.select(Kelma.id, Kelma.version)
        .where(
            Kelma.sort != None, Kelma.sort >= start + 1 + page * size, Kelma.sort < (start + 1 + page * size) + size
        )
        .order_by(Kelma.sort)
    ).scalars().all()
    return result


    
@kelma_api.route("/api/kelmas/get")
def kelmas_get():
    """It expects an query parameter ids that contain comma separated non negative integers
    it return 400 bad request if ids doesn't exist or not as specified
    note that if a specific id doesn't exist in db its discarded
    it returns a json list of Kelma objects that has the following properties:\n
    sort: int, this represents it is unique sort between all other kelmas\n
    id: int\n
    created_at: string, format example: 2025-09-12 12:33:00\n
    image_url: string\n
    display_name: string\n
    username: string\n
    content: string\n
    premium: bool\n"""
    
    ids_raw = request.args.get('ids')
    
    if ids_raw is None:
        abort(400)
    
    try:
        ids =  map(convert_to_id, ids_raw.split(','))
    except:
        abort(400)
    
    return db.session.execute(
        select(Kelma)
        .where(
            Kelma.id.in_(ids)
        )
        .order_by(Kelma.sort)
    ).scalars().all()
    
    
# @kelma_api.route("/api/kelma")
# def get_kelma():
#     """/api/kelma?username={username}|id={id} It gets a single kelma from the db and returns it
#     if kelma is not found it returns 404
#     """
#     id = get_int_from_url("id", default=None, min=0)
#     username = request.args.get("username")

#     if id and username:
#         result = get_kelma_local(id=id, username=username)
#     elif id:
#         result = get_kelma_local(id=id)
#     elif username:
#         result = get_kelma_local(username=username)
#     else:
#         abort(400)

#     if not result:
#         abort(404)

#     resp = make_response(json.dumps(result, default=ultra_serialize))
#     resp.content_type = "application/json"
#     return resp


# def get_kelma_local(**kwargs):
#     # kwargs are passed to filter by
#     images_dir_path = (
#         url_for(
#             "static", filename=current_app.config["PROFILE_IMGS_PATH"], _external=True
#         )
#         + "/"
#     )

#     subq = db.select(
#         func.row_number()
#         .over(order_by=Kelma.sort.asc() & Kelma.created_at.asc() & Kelma.id.asc())
#         .label("sort"),
#         Kelma.id,
#         Kelma.created_at,
#         (literal(images_dir_path) + Kelma.image_fn).label("image_url"),
#         Kelma.display_name,
#         Kelma.username,
#         Kelma.content,
#     ).subquery()

#     result = db.session.execute(
#         db.select(
#             subq.c.sort,
#             subq.c.id,
#             subq.c.created_at,
#             subq.c.image_url,
#             subq.c.display_name,
#             subq.c.username,
#             subq.c.content,
#         ).filter_by(**kwargs)
#     ).one_or_none()

#     return result


# POST api/kelma/
# PUT api/kelma/
# DELETE api/kelma/
