# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import json
from decimal import Decimal

import pytest
from django.conf import settings
from django.test import override_settings
from django.utils.translation import activate
from mock import patch
from shuup import configuration
from shuup.core.models import PaymentMethod
from shuup.testing import factories
from shuup.testing.factories import DEFAULT_IDENTIFIER
from shuup.testing.utils import apply_request_middleware

import shuup_stripe.utils.connect
from shuup_stripe.models import StripeCheckoutPaymentProcessor
from shuup_stripe.module import StripeCharger
from shuup_stripe.utils import (
    add_fee_to_payload, ensure_stripe_method_for_shop, ensure_stripe_token,
    get_amount_info, get_stripe_connect_url)
from shuup_stripe.views.oauth import stripe_oauth_callback

from .data import TOKEN_RETRIEVE_DATA
from .mocks import (
    mock_charge_create, mock_customer_create, mock_get_stripe_oauth_token,
    mock_token_retrieve)
from .utils import create_order_for_stripe


def init_test():
    activate("en")
    shop = factories.get_default_shop()
    shop.domain = "test"
    shop.save()
    factories.get_default_tax_class()
    return shop


@pytest.mark.django_db
def test_get_stripe_connect_url():
    shop = init_test()
    client_id = settings.STRIPE_OAUTH_CLIENT_ID

    with override_settings(STRIPE_OAUTH_CLIENT_ID=None):
        assert not get_stripe_connect_url(shop)

    with override_settings(STRIPE_CONNECT_REDIRECT_URI="https://localhost:8000"):
        url = get_stripe_connect_url(shop)
        assert "localhost" in url
        assert "client_id=%s" % client_id in url


@pytest.mark.django_db
def test_ensure_stripe_method_for_shop():
    shop = init_test()
    with override_settings(TAX_CLASS_SERVICES_IDENTIFIER=DEFAULT_IDENTIFIER):
        assert not PaymentMethod.objects.filter(shop=shop).count()
        assert not StripeCheckoutPaymentProcessor.objects.count()

        ensure_stripe_method_for_shop(shop, "derp")
        assert StripeCheckoutPaymentProcessor.objects.filter(enabled=True).count() == 1
        assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1

        ensure_stripe_method_for_shop(shop, "derp")
        assert StripeCheckoutPaymentProcessor.objects.filter(enabled=True).count() == 1
        assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1

        # inactivate
        StripeCheckoutPaymentProcessor.objects.update(enabled=False)
        PaymentMethod.objects.update(enabled=False)

        ensure_stripe_method_for_shop(shop, "derp")
        assert StripeCheckoutPaymentProcessor.objects.filter(enabled=True).count() == 1
        assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1


@pytest.mark.django_db
@patch.object(shuup_stripe.utils.connect, 'get_stripe_oauth_token', mock_get_stripe_oauth_token)
def test_ensure_stripe_token():
    shop = init_test()
    with override_settings(TAX_CLASS_SERVICES_IDENTIFIER=DEFAULT_IDENTIFIER):
        authorization_code = "ac_test_1231231"
        assert ensure_stripe_token(shop, authorization_code)
        data = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        assert data
        assert data["authorization_code"] == authorization_code

        assert ensure_stripe_token(shop)
        data = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        assert data
        assert "authorization_code" not in data

        # reset config
        configuration.set(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}")
        with override_settings(STRIPE_SECRET_KEY=None):
            assert not ensure_stripe_token(shop, authorization_code)  # stripe secret missing

        # no auth code available for refresh
        assert not ensure_stripe_token(shop, "refresh")


@pytest.mark.django_db
@patch.object(shuup_stripe.utils.connect, 'get_stripe_oauth_token', mock_get_stripe_oauth_token)
@pytest.mark.parametrize("maintenance_mode", [True, False])
def test_oauth_callback(rf, admin_user, maintenance_mode):
    shop = init_test()
    shop.maintenance_mode = maintenance_mode
    shop.save()

    with override_settings(TAX_CLASS_SERVICES_IDENTIFIER=DEFAULT_IDENTIFIER):

        # results admin redirect
        request = apply_request_middleware(rf.get("/", data={
            "code": "test",
            "state": "shop_id_%s" % shop.pk
        }), shop=shop)

        response = stripe_oauth_callback(request)
        assert response.status_code == 302
        assert response.url == "/sa/stripe/connect/"
        assert StripeCheckoutPaymentProcessor.objects.filter(enabled=True).count() == 1
        assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1

        new_url = "https://www.stripe.com"
        with override_settings(STRIPE_CONNECT_REDIRECT_ADMIN_URI=new_url):
            response = stripe_oauth_callback(request)
            assert response.status_code == 302
            assert response.url == new_url
            assert StripeCheckoutPaymentProcessor.objects.filter(enabled=True).count() == 1
            assert PaymentMethod.objects.filter(
                shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1

        # break it
        request = apply_request_middleware(rf.get("/"), shop=shop)
        view_func = stripe_oauth_callback
        response = view_func(request)
        assert response.status_code == 400

        request = apply_request_middleware(rf.get("/", data={"code": "123"}), shop=shop)
        response = view_func(request)
        assert response.status_code == 400

        request = apply_request_middleware(rf.get("/", data={"state": "123"}), shop=shop)
        response = view_func(request)
        assert response.status_code == 400

        request = apply_request_middleware(rf.get("/", data={"state": "123", "code": "123"}), shop=shop)
        response = view_func(request)
        assert response.status_code == 400

        # invalid shop id
        request = apply_request_middleware(rf.get("/", data={"state": "shop_id_100", "code": "123"}), shop=shop)
        response = view_func(request)
        assert response.status_code == 400

        request = apply_request_middleware(rf.post("/"), shop=shop)
        response = view_func(request)
        assert response.status_code == 400


@pytest.mark.django_db
@patch.object(shuup_stripe.utils.connect, 'get_stripe_oauth_token', mock_get_stripe_oauth_token)
@patch('stripe.Customer.create', mock_customer_create)
@patch('stripe.Charge.create', mock_charge_create)
@patch('stripe.Token.retrieve', mock_token_retrieve)
def test_connect_charge(rf):
    shop = init_test()
    authorization_code = "ac_test_1231231"
    with override_settings(TAX_CLASS_SERVICES_IDENTIFIER=DEFAULT_IDENTIFIER):
        ensure_stripe_token(shop, authorization_code)
        conf = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        ensure_stripe_method_for_shop(shop, conf["stripe_publishable_key"])
        payment_processor = StripeCheckoutPaymentProcessor.objects.filter(enabled=True).first()

        assert payment_processor
        assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1

        order = create_order_for_stripe(payment_processor, identifier="stripe_connect")
        token = TOKEN_RETRIEVE_DATA
        token_id = token["id"]
        order.shop = shop
        order.payment_data["stripe"] = {"token": token_id, "email": "test@example.com"}
        order.save()
        charger = StripeCharger(settings.STRIPE_SECRET_KEY, order)
        charger.create_charge()

        data = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        assert data  # connect worked


@pytest.mark.django_db
@pytest.mark.parametrize("original_amount, fee_percentage, expected_fee", [
    ("1000", None, None),
    ("1000", "10", 100),
    ("1230", "10", 123),
    ("50000", "10", 5000),
    ("12344", "12.8", 1580)
])
def test_add_fee_to_payload(original_amount, fee_percentage, expected_fee):
    shop = init_test()
    authorization_code = "ac_test_1231231"

    amount = Decimal(original_amount) / 100
    payload = dict(amount=original_amount)

    with override_settings(
            STRIPE_CONNECT_FEE_PERCENTAGE=fee_percentage, TAX_CLASS_SERVICES_IDENTIFIER=DEFAULT_IDENTIFIER):
        ensure_stripe_token(shop, authorization_code)
        conf = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        ensure_stripe_method_for_shop(shop, conf["stripe_publishable_key"])
        payment_processor = StripeCheckoutPaymentProcessor.objects.filter(enabled=True).first()

        assert payment_processor
        assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1
        price = shop.create_price(amount)
        order = create_order_for_stripe(payment_processor, identifier="stripe_connect", unit_price=price)
        token = TOKEN_RETRIEVE_DATA
        token_id = token["id"]
        order.shop = shop
        order.payment_data["stripe"] = {"token": token_id, "email": "test@example.com"}
        order.save()

        info = get_amount_info(price)
        info2 = get_amount_info(order.taxful_total_price)
        assert info["amount"] == info2["amount"]

        add_fee_to_payload(order, payload)
        if fee_percentage:
            assert payload["application_fee"] == expected_fee
        else:
            assert "application_fee" not in payload


@pytest.mark.django_db
@patch.object(shuup_stripe.utils.connect, 'get_stripe_oauth_token', mock_get_stripe_oauth_token)
def test_oauth_redirector(rf, admin_user):
    shop = init_test()
    with override_settings(
            TAX_CLASS_SERVICES_IDENTIFIER=DEFAULT_IDENTIFIER, STRIPE_OAUTH_REDIRECTOR="shuup_stripe_tests.utils:GoogleRedirector"):
        # results google redirect
        request = apply_request_middleware(rf.get("/", data={
            "code": "test",
            "state": "shop_id_%s" % shop.pk
        }), shop=shop)

        response = stripe_oauth_callback(request)
        assert response.status_code == 302
        assert response.url == "https://www.google.com"
