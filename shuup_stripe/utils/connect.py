# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import base64
import json
from decimal import Decimal

import requests
from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import override
from shuup import configuration
from shuup.core.models import FixedCostBehaviorComponent, PaymentMethod
from shuup.utils.importing import load
from six.moves.urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .general import get_amount_info

PAYMENT_CHOICE_IDENTIFIER = "stripe_connect"
PAYMENT_PROCESSOR_IDENTIFIER_FMT = "stripe_%(shop_id)s"


def get_stripe_connect_url(request, shop):
    if not settings.STRIPE_OAUTH_CLIENT_ID:
        return None
    base_url = "https://connect.stripe.com/oauth/authorize"
    stripe_url_provider = load(settings.STRIPE_URL_PROVIDER)()

    state = {
        "shop": shop.pk,
        "finalize_url": stripe_url_provider.get_oauth_finalize_url(request, shop)
    }
    kwargs = {
        "client_id": settings.STRIPE_OAUTH_CLIENT_ID,
        "state": encode_state(state),
        "stripe_user[business_type]": "company",
        "response_type": "code",
        "scope": "read_write",
        "redirect_uri": stripe_url_provider.get_oauth_callback_url(request, shop)
    }
    url_parts = list(urlparse(base_url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(kwargs)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def get_payment_method_for_shop(shop):
    return PaymentMethod.objects.filter(
        shop=shop,
        choice_identifier=PAYMENT_CHOICE_IDENTIFIER,
        payment_processor__identifier=PAYMENT_PROCESSOR_IDENTIFIER_FMT % dict(shop_id=shop.pk),
    ).first()


def ensure_stripe_method_for_shop(shop, publishable_key, tax_class, name, description="", price=None):
    from shuup_stripe.models import StripeCheckoutPaymentProcessor
    # activate processor due it was customer decision to "connect"
    payment_processor, created = StripeCheckoutPaymentProcessor.objects.update_or_create(
        identifier=PAYMENT_PROCESSOR_IDENTIFIER_FMT % dict(shop_id=shop.pk),
        defaults=dict(
            name="Stripe",
            secret_key=settings.STRIPE_SECRET_KEY,
            publishable_key=publishable_key,
            enabled=True
        )
    )
    payment_method = get_payment_method_for_shop(shop)
    if payment_method:
        # update the method to ensure it's fully working
        payment_method.enabled = True
        payment_method.tax_class = tax_class
        payment_method.name = name
        payment_method.description = description
        payment_method.save()

    else:
        payment_method = payment_processor.create_service(
            PAYMENT_CHOICE_IDENTIFIER,
            name=name,
            shop=shop,
            enabled=True,
            tax_class=tax_class,
            description=description
        )

    # also save the fallback language
    with override(settings.PARLER_DEFAULT_LANGUAGE_CODE):
        payment_method.set_current_language(settings.PARLER_DEFAULT_LANGUAGE_CODE)
        payment_method.name = name
        payment_method.description = description
        payment_method.save()

    component = payment_method.behavior_components.instance_of(FixedCostBehaviorComponent).first()
    if component:
        if price:
            component.price = price
            component.save()
        else:
            component.delete()

    elif price:
        payment_method.behavior_components.add(FixedCostBehaviorComponent.objects.create(price_value=price))

    return payment_method


def ensure_stripe_token(shop, authorization_code="refresh"):
    """
    Ensure stripe token is up to date

    If authorization code is not given, use one from database

    :param shop:
    :param authorization_code:
    :return:
    """
    if not hasattr(settings, "STRIPE_SECRET_KEY") or not settings.STRIPE_SECRET_KEY:
        return False

    stripe_data = get_stripe_oauth_data(shop)
    code = stripe_data.get("refresh_token") if authorization_code == "refresh" else authorization_code

    if not code:
        return False

    payload = {
        "client_secret": settings.STRIPE_SECRET_KEY,
    }
    if authorization_code != "refresh":
        payload["code"] = code
        payload["grant_type"] = "authorization_code"
    else:
        payload["refresh_token"] = code
        payload["grant_type"] = "refresh_token"

    response_data = get_stripe_oauth_token(payload)

    # TODO: Error handling
    error = response_data.get("error")
    if error:
        return False

    if authorization_code != "refresh":
        response_data["authorization_code"] = authorization_code

    set_stripe_oauth_data(shop, response_data)
    return True


def get_stripe_oauth_data(shop):
    return json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))


def set_stripe_oauth_data(shop, data):
    configuration.set(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, json.dumps(data))


def get_stripe_oauth_token(payload):
    response = requests.post("https://connect.stripe.com/oauth/token", data=payload)
    return json.loads(response.content.decode("utf-8"))


def add_fee_to_payload(order, payload):
    fee_percentage = getattr(settings, "STRIPE_CONNECT_FEE_PERCENTAGE", None)
    if not fee_percentage:
        return

    fee_percentage = Decimal(fee_percentage)
    amount = Decimal(payload["amount"]) / 100
    if fee_percentage > 0:
        payload["application_fee"] = get_amount_info(order.shop.create_price(amount * (fee_percentage / 100)))["amount"]


def encode_state(state):
    return force_text(base64.b64encode(force_bytes(json.dumps(state))))


def decode_state(state):
    from binascii import Error as BinasciiError
    try:
        return json.loads(force_text(base64.b64decode(force_text(state))))
    except (TypeError, BinasciiError, ValueError):
        return None
