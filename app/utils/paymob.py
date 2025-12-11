if __name__ == "__main__":
    import sys

    sys.path.append("D:\\dev\\projects\\kelma")

from app.secrets import (
    PAYMOB_SECRET_KEY,
    PAYMOB_INTEGRATIONS_IDS,
    PAYMOB_PUBLIC_KEY,
    PAYMOB_HMAC,
)
import requests as re
from typing import Callable
from functools import wraps
from flask import abort, request
import hmac
import json

# TODO: DOES INTENTION HAVE EXPIRATION TIME AND CAN WE SET IT ?

def create_intent(email: str, user_id: int, price_for_month: int, months: int):
    """This method creates an intent and returns its url"""

    url = "https://accept.paymob.com/v1/intention/"
    payload = {
        "amount": price_for_month * months * 100,
        "currency": "EGP",
        "payment_methods": PAYMOB_INTEGRATIONS_IDS,
        "customer": {
            "email": f"{email}",
        },
        "items": [
            {
                "name": "اشتراك مميز في أول 20 كلمة",
                "quantity": months,
                "amount": price_for_month * 100,
            },
        ],
        "billing_data": {
            "email": f"{email}",
            "first_name": "_",
            "last_name": "_",
            "phone_number": "_",
        },
        "extras": {
            "user_id": user_id
        }
    }
    headers = {
        "Authorization": f"Token {PAYMOB_SECRET_KEY}",
    }

    resp = re.post(url, json=payload, headers=headers)
    if resp.ok:
        client_secret = resp.json()["client_secret"]
        return f"https://accept.paymob.com/unifiedcheckout/?publicKey={PAYMOB_PUBLIC_KEY}&clientSecret={client_secret}"
    
    # TODO: LOG THIS AS ERROR
    print(resp.status_code)
    print(resp.text)
    raise Exception("intention creation response is not okay!")


def void_transaction(transaction_id: str) -> bool:
    """It voids a transaction and returns a boolean indicating success or not."""

    url = "https://accept.paymob.com/api/acceptance/void_refund/void"
    payload = json.dumps({"transaction_id": transaction_id})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {PAYMOB_SECRET_KEY}",
    }
    response = re.post(url, headers=headers, data=payload)

    # print("="*50)
    # print(response.ok)
    # print(response.status_code)
    # print(response.text)
    # print("="*50)

    return response.ok


def refund_transaction(transaction_id: str) -> bool:
    """It refunds a transaction and returns a boolean indicating success or not."""

    url = "https://accept.paymob.com/api/acceptance/void_refund/refund"
    payload = json.dumps({"transaction_id": transaction_id})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {PAYMOB_SECRET_KEY}",
    }
    response = re.post(url, headers=headers, data=payload)

    # print("="*50)
    # print(response.ok)
    # print(response.status_code)
    # print(response.text)
    # print("="*50)

    return response.ok


if __name__ == "__main__":
    print(create_intent("youness@gmail.com", 200, 3))

TRANSACTION_CONSIDERED_KEYS = [
    "obj.amount_cents",
    "obj.created_at",
    "obj.currency",
    "obj.error_occured",
    "obj.has_parent_transaction",
    "obj.id",
    "obj.integration_id",
    "obj.is_3d_secure",
    "obj.is_auth",
    "obj.is_capture",
    "obj.is_refunded",
    "obj.is_standalone_payment",
    "obj.is_voided",
    "obj.order.id",
    "obj.owner",
    "obj.pending",
    "obj.source_data.pan",
    "obj.source_data.sub_type",
    "obj.source_data.type",
    "obj.success",
]

TOKEN_CONSIDERED_KEYS = [
    "obj.card_subtype",
    "obj.created_at",
    "obj.email",
    "obj.id",
    "obj.masked_pan",
    "obj.merchant_id",
    "obj.order_id",
    "obj.token",
]

REDIRECT_CONSIDERED_KEYS = [
    "amount_cents",
    "created_at",
    "currency",
    "error_occured",
    "has_parent_transaction",
    "id",
    "integration_id",
    "is_3d_secure",
    "is_auth",
    "is_capture",
    "is_refunded",
    "is_standalone_payment",
    "is_voided",
    "order",
    "owner",
    "pending",
    "source_data.pan",
    "source_data.sub_type",
    "source_data.type",
    "success",
]


def get_sorted_json_message(
    data_dict: dict, considered_keys: list, split: str | None = "."
) -> str:
    message_parts_list: list[str] = []

    for key in considered_keys:
        value = data_dict
        for key2 in key.split(split):
            value = value[key2]
        if not isinstance(value, str):
            value = json.dumps(value)
        message_parts_list.append(value)

    return "".join(message_parts_list)


def paymob_hmac_security(view: Callable):
    @wraps(view)
    def new_view(*args, **kwargs):
        if request.method == "GET":
            msg = get_sorted_json_message(request.args, REDIRECT_CONSIDERED_KEYS, None)
        elif request.method == "POST" and request.json["type"] == "TRANSACTION":
            msg = get_sorted_json_message(request.json, TRANSACTION_CONSIDERED_KEYS)
        elif request.method == "POST" and request.json["type"] == "TOKEN":
            msg = get_sorted_json_message(request.json, TOKEN_CONSIDERED_KEYS)
        else:
            abort(400)

        hmac_obj = hmac.new(PAYMOB_HMAC, msg.encode(), "sha512")
        my_hmac = hmac_obj.hexdigest()
        sent_hmac = request.args.get("hmac")

        if my_hmac == sent_hmac:
            return view()
        else:
            abort(403)

    return new_view


# LAST PAYMENT STATUS CODES
PAYMENT_STATUS_CODE = {
    "SUCCESS_EXTEND": 0,
    "SUCCESS_SUBSCRIBE": 1,
    "ERROR_FULL": 2,
    "ERROR_UNKNOWN": 3
}

# password reset link (using email)

# first_part                                                                   second_part
# signed_by_secret_key and identifies the user uniquely and creation time      a random string that to know the last sent link to the user

# then user can update his password successfully!

# change password
# it is easy as long as the user knows his old password.