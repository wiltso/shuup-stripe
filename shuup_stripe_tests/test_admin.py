# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import json

import mock
import pytest
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import override_settings
from django.test.client import Client
from shuup import configuration
from shuup.admin.shop_provider import SHOP_SESSION_KEY
from shuup.core.models import PaymentMethod
from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware
from shuup.utils.importing import load
from six.moves.urllib.parse import parse_qsl, urlparse

import shuup_stripe.utils.connect
from shuup_stripe.models import StripeCheckoutPaymentProcessor
from shuup_stripe.utils import get_payment_method_for_shop
from shuup_stripe.utils.connect import (
    decode_state, get_stripe_oauth_data, set_stripe_oauth_data
)
from shuup_stripe_tests.utils import SmartClient

from .mocks import mock_get_stripe_oauth_token


def set_client_shop(client, shop):
    session = client.session
    session[SHOP_SESSION_KEY] = shop.id
    session.save()


@pytest.mark.django_db
@override_settings(SHUUP_ENABLE_MULTIPLE_SHOPS=True)
def test_help_blocks(admin_user):
    shop1 = factories.get_shop(identifier="shop1", name="Shop 1", domain="shop-1")
    shop2 = factories.get_shop(identifier="shop2", name="Shop 2", domain="shop-2")

    shop1.staff_members.add(admin_user)
    shop2.staff_members.add(admin_user)

    client = Client()
    client.login(username=admin_user.username, password="password")

    # use shop2
    set_client_shop(client, shop2)

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        retrieve_mocked.return_value = None

        response = client.get(reverse("shuup_admin:home"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Connect your Stripe account to Shuup store. Once connected, you are able to receive payments." in content
        assert "Connect Stripe" in content
        assert reverse("shuup_admin:shuup_stripe.connect") in content

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        data = {"id": "123456", "stripe_user_id": "123456"}
        # set some setting to make the help block 'done'
        set_stripe_oauth_data(shop2, data)
        retrieve_mocked.return_value = data

        response = client.get(reverse("shuup_admin:home"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Re-connect Stripe" in content
        assert reverse("shuup_admin:shuup_stripe.connect") in content


@pytest.mark.django_db
@override_settings(
    SHUUP_ENABLE_MULTIPLE_SHOPS=True,
    SHUUP_SETUP_WIZARD_PANE_SPEC=["shuup.admin.modules.service_providers.views.PaymentWizardPane"]
)
def test_wizard_form(admin_user):
    shop1 = factories.get_shop(identifier="shop1", name="Shop 1", domain="shop-1", maintenance_mode=False)
    shop2 = factories.get_shop(identifier="shop2", name="Shop 2", domain="shop-2", maintenance_mode=False)

    shop1.staff_members.add(admin_user)
    shop2.staff_members.add(admin_user)

    client = Client()
    client.login(username=admin_user.username, password="password")

    # use shop2
    set_client_shop(client, shop2)

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        retrieve_mocked.return_value = None

        response = client.get(reverse("shuup_admin:wizard") + "?pane_id=payment")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Accept credit cards using" in content
        assert "https://stripe.com/" in content
        assert "Don't have a Stripe account?" in content

        payment_processor = StripeCheckoutPaymentProcessor.objects.create(secret_key="secret", publishable_key="12", name="Stripe")

        response = client.get(reverse("shuup_admin:wizard") + "?pane_id=payment")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        payment_processor.create_service(None, shop=shop2, tax_class=factories.get_default_tax_class(), enabled=True, name="Stripe")
        response = client.get(reverse("shuup_admin:wizard") + "?pane_id=payment")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        assert 'name="stripe-service_name"' in content
        assert 'name="stripe-secret_key"' in content
        assert 'name="stripe-publishable_key"' in content


@pytest.mark.django_db
@override_settings(SHUUP_ENABLE_MULTIPLE_SHOPS=True)
def test_connect_stripe(admin_user):
    shop1 = factories.get_shop(identifier="shop1", name="Shop 1", domain="shop-1", maintenance_mode=False)
    shop2 = factories.get_shop(identifier="shop2", name="Shop 2", domain="shop-2", maintenance_mode=False)

    shop1.staff_members.add(admin_user)
    shop2.staff_members.add(admin_user)

    client = Client()
    client.login(username=admin_user.username, password="password")

    # use shop2
    set_client_shop(client, shop2)

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        retrieve_mocked.return_value = {"id": "123", "stripe_user_id": "123"}

        response = client.get(reverse("shuup_admin:shuup_stripe.connect"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Connect with Stripe" in content

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        data = {"id": "123456", "stripe_user_id": "123456"}
        # set some setting to make the help block 'done'
        set_stripe_oauth_data(shop2, data)
        retrieve_mocked.return_value = data

        response = client.get(reverse("shuup_admin:shuup_stripe.connect"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Stripe Account Status" in content


@pytest.mark.django_db
@override_settings(SHUUP_ENABLE_MULTIPLE_SHOPS=True)
def test_finalize_stripe(admin_user):
    shop1 = factories.get_shop(identifier="shop1", name="Shop 1", domain="shop-1", maintenance_mode=False)
    shop2 = factories.get_shop(identifier="shop2", name="Shop 2", domain="shop-2", maintenance_mode=False)

    shop1.staff_members.add(admin_user)
    shop2.staff_members.add(admin_user)

    client = Client()
    client.login(username=admin_user.username, password="password")

    # use shop2
    set_client_shop(client, shop2)
    assert not get_payment_method_for_shop(shop2)

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        data = {"id": "123", "stripe_user_id": "123", "stripe_publishable_key": "key"}
        retrieve_mocked.return_value = data
        set_stripe_oauth_data(shop2, data)

        response = client.get(reverse("shuup_admin:shuup_stripe.finalize"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Stripe has now been connected. Please fill the form below to continue." in content

        tax_class = factories.get_default_tax_class()

        response = client.post(reverse("shuup_admin:shuup_stripe.finalize"), data={
            "tax_class": tax_class.id,
            "name": "Stripe",
            "description": "Desc",
            "price": 1
        })
        assert response.status_code == 302
        assert response.url == reverse("shuup_admin:shuup_stripe.connect")

        response = client.get(reverse("shuup_admin:shuup_stripe.finalize"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert '<option value="%d" selected>%s' % (tax_class.pk, tax_class.name) in content
        assert '<input type="text" name="name" value="Stripe"' in content
        assert '<input type="number" name="price" value="1.000000000"' in content


@pytest.mark.django_db
@mock.patch.object(shuup_stripe.utils.connect, "get_stripe_oauth_token", mock_get_stripe_oauth_token)
@override_settings(SHUUP_ENABLE_MULTIPLE_SHOPS=True)
def test_finalize_stripe_flow(admin_user, rf):
    shop1 = factories.get_shop(identifier="shop1", name="Shop 1", domain="shop-1", maintenance_mode=False)
    shop2 = factories.get_shop(identifier="shop2", name="Shop 2", domain="shop-2", maintenance_mode=False)

    shop1.staff_members.add(admin_user)
    shop2.staff_members.add(admin_user)

    client = SmartClient()
    client.login(username=admin_user.username, password="password")

    # use shop2
    shop = shop2
    configuration.set(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, json.dumps({}))

    set_client_shop(client, shop)
    assert not get_payment_method_for_shop(shop)
    stripe_url_provider = load(settings.STRIPE_URL_PROVIDER)()

    with mock.patch("stripe.Account.retrieve") as retrieve_mocked:
        data = {"id": "123", "stripe_user_id": "123", "stripe_publishable_key": "key"}
        retrieve_mocked.return_value = data

        response, soup = client.response_and_soup(reverse("shuup_admin:shuup_stripe.connect"))
        assert response.status_code == 200
        connect_link = soup.find("a", {"id": "stripe-connect-btn"}).get("href")
        connect_url = urlparse(connect_link)
        query = dict(parse_qsl(connect_url.query))
        state = decode_state(query["state"])
        redirect_uri = query["redirect_uri"]
        finalize_url = state["finalize_url"]

        assert state["shop"] == shop.pk
        request = apply_request_middleware(rf.get("/"))

        assert finalize_url.endswith(stripe_url_provider.get_oauth_finalize_url(request, shop))
        assert redirect_uri.endswith(stripe_url_provider.get_oauth_callback_url(request, shop))
        assert PaymentMethod.objects.count() == 0

        # instead of accessing the connect_link, we call redirect_uri directly, passing the access token
        # to prevent having a real Stripe account for this test. we just want to test the flow itself.
        stripe_payload = {
            "code": "123-AUTH-CODE",
            "state": query["state"]
        }
        assert not get_stripe_oauth_data(shop)
        response = client.get(redirect_uri, data=stripe_payload)
        assert response.status_code == 302
        assert urlparse(response.url).path == urlparse(finalize_url).path

        stripe_data = get_stripe_oauth_data(shop)
        assert stripe_data["authorization_code"] == stripe_payload["code"]

        # invoke the callback url
        finalize_url_2 = response.url
        response = client.get(finalize_url_2)
        content = response.content.decode("utf-8")
        assert "Stripe has now been connected. Please fill the form below to continue." in content

        finalize_data = {
            "tax_class": factories.get_default_tax_class().pk,
            "name": "Stripe",
            "description": "Desc",
            "price": 1
        }
        response = client.post(finalize_url_2, data=finalize_data)
        assert response.status_code == 302
        assert response.url == reverse("shuup_admin:shuup_stripe.connect")
        payment_method = get_payment_method_for_shop(shop)
        assert payment_method
        assert payment_method.tax_class.pk == finalize_data["tax_class"]
        assert payment_method.name == finalize_data["name"]
        assert payment_method.description == finalize_data["description"]
