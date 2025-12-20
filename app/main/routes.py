from flask import (
    render_template,
    url_for,
    current_app,
    redirect,
    request,
)
from app.main import main
from app import db
from app.models import Kelma, Order
from app.utils.auth import get_user, login_required
from app.main.forms import (
    KelmasSearchForm,
    KelmaForm,
    PremiumKelmaForm,
    ExtendReserveForm,
    IMAGE_MIMES_STR,
)
from flask import g
from app.utils.main import (
    save_thumbnail,
    get_random_sort,
    ceil_datetime,
    shift_sort_from,
    shift_sort_back_after,
    update_kelma_image,
    get_premium_count,
    get_first_available_date,
    delete_kelma,
    extend_kelma_reserve_end,
)
from datetime import datetime, timedelta
from app.exceptions import NoUserInDb, NoUserInSession
from app.utils.paymob import (
    paymob_hmac_security,
    create_intent,
    void_transaction,
    refund_transaction,
    PAYMENT_STATUS_CODE,
)
from datetime import date
from app.models import User
from app.utils.filters import readable_date, arabic_pluralize
from app import csrf
from typing import cast
from flask_wtf.file import FileRequired
from werkzeug.datastructures import FileStorage
from sqlalchemy import select

@main.route("/")
def home():
    # form = KelmasSearchForm()

    try:
        user = get_user()
    except (NoUserInSession, NoUserInDb):
        return render_template("home-out.html.j2")

    kelma = user.public_kelma
    kelma_json = current_app.json.dumps(kelma)
    return render_template(
        "home-in.html.j2", kelma=kelma, kelma_json=kelma_json
    )


@main.get("/kelma")
@login_required
def kelma_get():
    def resp():
        return kelma_get_or_fail_response(
            kelma=kelma, form=form, extend_form=extend_form
        )

    kelma = g.user.public_kelma

    if kelma is None or kelma.normal:
        form = KelmaForm(obj=kelma)
        extend_form = None
    else:
        form = PremiumKelmaForm(obj=kelma)
        extend_form = ExtendReserveForm()
    return resp()


@main.post("/kelma")
@login_required
def kelma_post():
    kelma = g.user.kelma

    if kelma is None or kelma.sort is None or kelma.normal:
        return new_or_normal_kelma_post(kelma)
    else:
        return premium_kelma_post(kelma)


def new_or_normal_kelma_post(kelma):
    def success_response():
        return redirect(url_for("main.home"))

    def error_response(premium_count=None, first_available_date=None, **kwargs):
        return kelma_get_or_fail_response(
            premium_count,
            first_available_date,
            form=form,
            kelma=g.user.public_kelma,
            error_msg=error_msg,
            **kwargs,
        )

    form = KelmaForm()
    error_msg = None

    if kelma is None:
        kelma = Kelma(username=g.user.username)
        db.session.add(kelma)

    if form.delete.data:
        delete_kelma(kelma)
        db.session.commit()
        return success_response()

    extra_validators = {}

    if kelma.image_fn is None or kelma.sort is None:
        extra_validators["image"] = [FileRequired("هذا الحقل مطلوب!")]

    if not form.validate(extra_validators):
        if form.image.errors:
            error_msg = form.image.errors[0]
            form.image.errors = []
        return error_response()

    if not update_kelma_image(kelma, form.image.data):
        error_msg = "حدثت مشكلة أثناء تحميل هذه الصورة!"
        return error_response()

    kelma.display_name = form.display_name.data
    kelma.content = form.content.data
    
    if kelma.version is not None:
        kelma.version += 1
        
    if form.kelma_type.data == "top_twenty":
        premium_count = get_premium_count()
        if premium_count >= current_app.config["PREMIUM_COUNT"]:
            error_msg = f"قائمة أول {current_app.config["PREMIUM_COUNT"]} ممتلئة حاليا!"
            return error_response(premium_count)
        else:
            if current_app.config["FREE_PREMIUM_KELMAS"]:
                activate_premium_kelma(kelma, form.reserve_length.data)
                db.session.commit()
                return success_response()
            else:
                db.session.commit()
                return go_to_payment(form.reserve_length.data)

    elif form.kelma_type.data == "normal" and kelma.sort == None:
        random_sort = get_random_sort()
        shift_sort_from(random_sort)
        kelma.sort = random_sort

    db.session.commit()
    return success_response()


def premium_kelma_post(kelma):
    def success_response():
        return redirect(url_for("main.home"))

    def error_response(premium_count=None, first_available_date=None, **kwargs):
        return kelma_get_or_fail_response(
            premium_count,
            first_available_date,
            form=form,
            extend_form=extend_form,
            kelma=g.user.public_kelma,
            error_msg=error_msg,
            extend_error_msg=extend_error_msg,
            **kwargs,
        )

    form = PremiumKelmaForm()
    extend_form = ExtendReserveForm()
    error_msg = None
    extend_error_msg = None

    if form.delete.data:
        delete_kelma(kelma)
        db.session.commit()
        return success_response()

    if extend_form.extend.data:
        if extend_form.validate():
            if current_app.config["FREE_PREMIUM_KELMAS"]:
                extend_error_msg = "لا يمكن تمديد الحجز في مرحلة ال BETA"
                return error_response()
            else:
                return go_to_payment(extend_form.reserve_length.data)
        else:
            return error_response()

    if not form.validate():
        if form.image.errors:
            error_msg = form.image.errors[0]
            form.image.errors = []
        return error_response()

    if not update_kelma_image(kelma, form.image.data):
        error_msg = "حدثت مشكلة أثناء تحميل هذه الصورة!"
        return error_response()

    kelma.display_name = form.display_name.data
    kelma.content = form.content.data
    
    if kelma.version is not None:
        kelma.version += 1
        
    db.session.commit()
    return success_response()


def go_to_payment(reserve_length):
    url = create_intent(
        g.user.email, g.user.id, current_app.config["PRICE_FOR_MONTH"], reserve_length
    )
    return redirect(url)

def activate_premium_kelma(kelma, months):
    premium = get_premium_count()
    if premium < current_app.config["PREMIUM_COUNT"]:
        old_sort = kelma.sort
        if old_sort != None:
            kelma.sort = None
            shift_sort_back_after(old_sort)
        sort = premium + 1
        shift_sort_from(sort)
        kelma.sort = sort
        extend_kelma_reserve_end(kelma, months)

def kelma_get_or_fail_response(premium_count=None, first_available_date=None, **kwargs):
    if premium_count == None:
        premium_count = get_premium_count()
    if premium_count >= current_app.config["PREMIUM_COUNT"] and first_available_date == None:
        first_available_date = get_first_available_date()

    return render_template(
        "kelma.html.j2",
        images_mimes=IMAGE_MIMES_STR,
        price_for_month=current_app.config["PRICE_FOR_MONTH"],
        top_allowed=premium_count < current_app.config["PREMIUM_COUNT"],
        first_available_date=first_available_date,
        free_premium=current_app.config["FREE_PREMIUM_KELMAS"],
        **kwargs,
    )


@main.route("/payment-redirect")
@paymob_hmac_security
def payment_redirect():
    if request.args["success"]:
        order_id = request.args["order"]
        order = db.session.get(Order, order_id)
        if not order or order.status_code == PAYMENT_STATUS_CODE["ERROR_UNKNOWN"]:
            # TODO: LOG AS ERROR
            msg = "لقد حدثت مشكلة غير متوقعة برجاء التواصل مع الدعم"
            redirect_to_home = False
        elif order.status_code == PAYMENT_STATUS_CODE["SUCCESS_SUBSCRIBE"]:
            msg = f"لقد تم اشتراكك في أول {current_app.config["PREMIUM_COUNT"]} كلمة بنجاح لمدة {arabic_pluralize('شهر', 'أشهر', order.months)} حتى تاريخ {readable_date(cast(date, order.reserve_end))}"
            redirect_to_home = True
        elif order.status_code == PAYMENT_STATUS_CODE["SUCCESS_EXTEND"]:
            msg = f"لقد تم تمديد اشتراكك بنجاح لمدة {arabic_pluralize('شهر', 'أشهر', order.months)} حتى تاريخ {readable_date(cast(date, order.reserve_end))}"
            redirect_to_home = True
        elif order.status_code == PAYMENT_STATUS_CODE["ERROR_FULL"]:
            msg = (
                f"معذرة, ولكن قائمة أول {current_app.config["PREMIUM_COUNT"]} كلمة ممتلئة حاليا ولقد تم اعادة المبلغ لحسابك"
            )
            redirect_to_home = False
    else:
        msg = "لقد فشلت عملية الدفع!"
        redirect_to_home = True

    return render_template(
        "payment-redirect.html.j2", msg=msg, redirect_to_home=redirect_to_home
    )


@main.route("/payment-process", methods=["POST"])
@csrf.exempt
@paymob_hmac_security
def payment_process():
    if request.json["type"] == "TOKEN":
        ...
    elif request.json["type"] == "TRANSACTION" and request.json["obj"]["is_voided"]:
        ...
    elif request.json["type"] == "TRANSACTION" and request.json["obj"]["is_refunded"]:
        ...
    elif request.json["type"] == "TRANSACTION" and request.json["obj"]["success"]:
        order_id = request.json["obj"]["order"]["id"]
        user_id = request.json["obj"]["payment_key_claims"]["extra"]["user_id"]
        email = request.json["obj"]["order"]["shipping_data"]["email"]
        price_for_month = (
            request.json["obj"]["order"]["items"][0]["amount_cents"] // 100
        )
        months = request.json["obj"]["order"]["items"][0]["quantity"]
        order = Order(
            id=order_id,
            user_id=user_id,
            price_for_month=price_for_month,
            email=email,
            months=months,
        )
        db.session.add(order)
        db.session.commit()

        user = db.session.execute(select(User).where(User.id == user_id)).scalar_one()
        kelma = user.kelma
        
        if kelma.reserve_end == None:
            premium = get_premium_count()
            if premium < current_app.config["PREMIUM_COUNT"]:
                activate_premium_kelma(kelma, months)
                order.reserve_end = kelma.reserve_end
                order.status_code = PAYMENT_STATUS_CODE["SUCCESS_SUBSCRIBE"]
                db.session.commit()
            else:
                id = str(request.json["obj"]["id"])
                if void_transaction(id) or refund_transaction(id):
                    order.status_code = PAYMENT_STATUS_CODE["ERROR_FULL"]
                    db.session.commit()
        else:
            extend_kelma_reserve_end(kelma, months)
            order.reserve_end = kelma.reserve_end
            order.status_code = PAYMENT_STATUS_CODE["SUCCESS_EXTEND"]
            db.session.commit()

    return ""
