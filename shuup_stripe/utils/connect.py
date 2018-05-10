# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import json
from decimal import Decimal

import requests
from django.conf import settings
from shuup import configuration
from shuup.core.models import PaymentMethod, TaxClass

from .general import get_amount_info

try:
    import urlparse
    from urllib import urlencode
except:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode


def get_stripe_connect_url(shop):
    if not settings.STRIPE_OAUTH_CLIENT_ID:
        return None
    base_url = "https://connect.stripe.com/oauth/authorize"
    kwargs = {
        "client_id": settings.STRIPE_OAUTH_CLIENT_ID,
        "state": "shop_id_%s" % shop.pk,
        "stripe_user[business_type]": "company",
        "response_type": "code",
        "scope": "read_write"
    }
    if hasattr(settings, "STRIPE_CONNECT_REDIRECT_URI") and settings.STRIPE_CONNECT_REDIRECT_URI:
        kwargs["redirect_uri"] = settings.STRIPE_CONNECT_REDIRECT_URI
    url_parts = list(urlparse.urlparse(base_url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(kwargs)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)


def ensure_stripe_method_for_shop(shop, publishable_key):
    from shuup_stripe.models import StripeCheckoutPaymentProcessor
    # activate processor due it was customer decision to "connect"
    payment_processor, created = StripeCheckoutPaymentProcessor.objects.update_or_create(
        identifier="stripe_%s" % shop.pk,
        defaults=dict(
            name="",
            secret_key=settings.STRIPE_SECRET_KEY,
            publishable_key=publishable_key,
            enabled=True
        )
    )
    tax_class = TaxClass.objects.get(identifier=settings.TAX_CLASS_SERVICES_IDENTIFIER)
    payment_method = PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect").first()
    if not payment_method:
        payment_method = payment_processor.create_service(
            "stripe_connect",
            name="Stripe",
            shop=shop,
            enabled=True,
            tax_class=tax_class,
            description=""
        )
    else:
        # update the method to ensure it's fully working
        payment_method.enabled = True
        payment_method.tax_class = tax_class
        payment_method.save()

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

    stripe_data = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
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

    configuration.set(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, json.dumps(response_data))
    return True


def get_stripe_oauth_token(payload):
    response = requests.post("https://connect.stripe.com/oauth/token", data=payload)
    return json.loads(response.content.decode("utf-8"))


def add_fee_to_payload(order, payload):
    if not hasattr(settings, "STRIPE_CONNECT_FEE_PERCENTAGE"):
        return
    fee_percentage = settings.STRIPE_CONNECT_FEE_PERCENTAGE
    if fee_percentage is None:
        return

    fee_percentage = Decimal(fee_percentage)
    amount = Decimal(payload["amount"]) / 100
    if fee_percentage > 0:
        payload["application_fee"] = get_amount_info(order.shop.create_price(amount * (fee_percentage / 100)))["amount"]
