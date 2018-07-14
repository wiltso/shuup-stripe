# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import json
from decimal import Decimal

import pytest
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import override_settings
from django.utils.translation import activate
from mock import patch
from shuup import configuration
from shuup.core.models import FixedCostBehaviorComponent, PaymentMethod
from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware
from shuup.utils.excs import Problem
from six.moves.urllib.parse import parse_qsl, urlparse

import shuup_stripe.utils.connect
from shuup_stripe.models import StripeCheckoutPaymentProcessor
from shuup_stripe.module import StripeCharger
from shuup_stripe.utils import (
    add_fee_to_payload, decode_state, encode_state,
    ensure_stripe_method_for_shop, ensure_stripe_token, get_amount_info,
    get_payment_method_for_shop, get_stripe_connect_url
)
from shuup_stripe.views.oauth import stripe_oauth_callback

from .data import TOKEN_RETRIEVE_DATA
from .mocks import (
    mock_charge_create, mock_customer_create, mock_get_stripe_oauth_token,
    mock_token_retrieve
)
from .utils import create_order_for_stripe


def init_test():
    activate("en")
    shop = factories.get_default_shop()
    shop.domain = "test"
    shop.save()
    return shop


@pytest.mark.django_db
def test_get_stripe_connect_url(rf):
    shop = init_test()
    client_id = settings.STRIPE_OAUTH_CLIENT_ID

    from shuup_stripe.url_provider import StripeURLProvider
    url_provider = StripeURLProvider()
    request = apply_request_middleware(rf.get("/"))
    finalize_url = url_provider.get_oauth_finalize_url(request, shop)

    with override_settings(STRIPE_OAUTH_CLIENT_ID=None):
        assert not get_stripe_connect_url(request, shop)

    url = get_stripe_connect_url(request, shop)
    assert "client_id=%s" % client_id in url
    querystring = dict(parse_qsl(urlparse(url).query))
    state = querystring["state"]
    decoded_state = decode_state(state)
    assert decoded_state["shop"] == shop.id
    assert decoded_state["finalize_url"] == finalize_url


@pytest.mark.parametrize("payment_name, description, price", [
    ("Stripe free", "Nice desc", 10),
    ("Stripe free", "Nice desc", 0),
])
@pytest.mark.django_db
def test_ensure_stripe_method_for_shop(payment_name, description, price):
    shop = init_test()
    assert not PaymentMethod.objects.filter(shop=shop).count()
    assert not StripeCheckoutPaymentProcessor.objects.count()

    for time in range(2):
        ensure_stripe_method_for_shop(shop, "derp", factories.get_default_tax_class(), payment_name, description, price)
        payment = get_payment_method_for_shop(shop)
        assert payment
        assert payment.name == payment_name
        assert payment.description == description

        if price:
            component = payment.behavior_components.instance_of(FixedCostBehaviorComponent).first()
            assert component.price_value == price
        else:
            assert not payment.behavior_components.instance_of(FixedCostBehaviorComponent).exists()

    # make price zero
    ensure_stripe_method_for_shop(shop, "derp", factories.get_default_tax_class(), payment_name, description, 0)
    payment = get_payment_method_for_shop(shop)
    assert payment
    assert not payment.behavior_components.instance_of(FixedCostBehaviorComponent).exists()


@pytest.mark.django_db
@patch.object(shuup_stripe.utils.connect, 'get_stripe_oauth_token', mock_get_stripe_oauth_token)
def test_ensure_stripe_token():
    shop = init_test()
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

    from shuup_stripe.url_provider import StripeURLProvider
    url_provider = StripeURLProvider()
    finalize_url = url_provider.get_oauth_finalize_url(apply_request_middleware(rf.get("/")), shop)
    assert finalize_url.endswith(reverse("shuup_admin:shuup_stripe.finalize"))

    # results admin redirect
    request = apply_request_middleware(rf.get("/", data={
        "code": "test",
        "state": encode_state({"shop": shop.id, "finalize_url": finalize_url})
    }), shop=shop)

    response = stripe_oauth_callback(request)
    assert response.status_code == 302
    assert response.url.startswith(finalize_url)
    assert StripeCheckoutPaymentProcessor.objects.filter(enabled=True).count() == 0
    assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 0

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

    request = apply_request_middleware(rf.get("/", data={"state": encode_state({"shop": 1234})}), shop=shop)
    response = view_func(request)
    assert response.status_code == 400

    request = apply_request_middleware(rf.get("/", data={"state": "123", "code": "42423"}), shop=shop)
    response = view_func(request)
    assert response.status_code == 400

    # invalid shop id
    request = apply_request_middleware(rf.get("/", data={
        "code": 123,
        "state": encode_state({"shop": 53243, "finalize_url": "dsadas"})
    }), shop=shop)
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
def test_connect_charge():
    shop = init_test()
    authorization_code = "ac_test_1231231"
    ensure_stripe_token(shop, authorization_code)
    conf = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
    ensure_stripe_method_for_shop(shop, conf["stripe_publishable_key"], factories.get_default_tax_class(), "Payment")
    payment_processor = StripeCheckoutPaymentProcessor.objects.filter(enabled=True).first()

    assert payment_processor
    assert PaymentMethod.objects.filter(shop=shop, choice_identifier="stripe_connect", enabled=True).count() == 1

    order = create_order_for_stripe(payment_processor, identifier="stripe_connect")
    token = TOKEN_RETRIEVE_DATA
    token_id = token["id"]
    order.shop = shop
    order.payment_data["stripe"] = {"token": token_id, "email": "test@example.com"}
    order.save()

    retry_request_data = {
        "id": "1234",
        "paid": True
    }

    with patch("shuup.utils.http.retry_request") as retry_request_mocked:
        retry_request_mocked.return_value = retry_request_data
        charger = StripeCharger("secret", order)
        charger.create_charge()
        assert order.payments.exists()

    order2 = create_order_for_stripe(payment_processor, identifier="stripe")
    order2.shop = shop
    order2.payment_data["stripe"] = {"token": token_id, "email": "test@example.com"}
    order2.save()

    with patch("shuup.utils.http.retry_request") as retry_request_mocked:
        retry_request_mocked.return_value = retry_request_data
        charger = StripeCharger("secret", order2)
        charger.create_charge()
        assert order2.payments.exists()

    # errors
    order3 = create_order_for_stripe(payment_processor, identifier="stripe")
    order3.shop = shop
    order3.payment_data["stripe"] = {"token": token_id, "email": "test@example.com"}
    order3.save()

    with patch("shuup.utils.http.retry_request") as retry_request_mocked:
        retry_request_mocked.return_value = {}
        charger = StripeCharger("secret", order3)

        with pytest.raises(Problem) as exc:
            charger = StripeCharger("secret", order3)
            charger.create_charge()
        assert "Stripe Charge does not say 'paid'" in str(exc)

    with patch("shuup.utils.http.retry_request") as retry_request_mocked:
        # error #1
        retry_request_mocked.return_value = {
            "error": {"message": "true", "type": "critical"}
        }
        with pytest.raises(Problem) as exc:
            charger = StripeCharger("secret", order2)
            charger.create_charge()
        assert "Stripe: true (critical)" in str(exc)

        # error #2
        retry_request_mocked.return_value = {
            "failure_code": 123,
            "failure_message": "hahaha"
        }
        with pytest.raises(Problem) as exc:
            charger = StripeCharger("secret", order2)
            charger.create_charge()
        assert "Stripe: hahaha (123)" in str(exc)


@pytest.mark.django_db
@pytest.mark.parametrize("original_amount, fee_percentage, expected_fee", [
    ("1000", None, None),
    ("1000", "10", 100),
    ("1230", "10", 123),
    ("50000", "10", 5000),
    ("12344", "12.8", 1580)
])
def test_add_fee_to_payload(original_amount, fee_percentage, expected_fee):
    with override_settings(STRIPE_CONNECT_FEE_PERCENTAGE=fee_percentage):
        shop = init_test()
        authorization_code = "ac_test_1231231"

        amount = Decimal(original_amount) / 100
        payload = dict(amount=original_amount)

        ensure_stripe_token(shop, authorization_code)
        conf = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        ensure_stripe_method_for_shop(shop, conf["stripe_publishable_key"], factories.get_default_tax_class(), "Payment")
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
