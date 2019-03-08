# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import mock
import pytest
from shuup.core import cache
from shuup.front.basket import get_basket
from shuup.testing import factories
from shuup.testing.factories import get_default_shop, get_default_tax_class
from shuup.testing.utils import apply_request_middleware

from shuup_stripe.checkout_phase import StripeCheckoutPhase
from shuup_stripe.models import StripeCheckoutPaymentProcessor
from shuup_stripe.utils import (
    set_checkout_payment_details_message, set_checkout_payment_phase_message,
    set_checkout_saved_card_message
)


@pytest.mark.django_db
def test_stripe_checkout_phase(rf):
    cache.clear()
    shop = factories.get_default_shop()
    contact = factories.create_random_person()
    request = apply_request_middleware(rf.post("/"), shop=get_default_shop())
    request.session = {}
    request.basket = get_basket(request)

    payment_processor = StripeCheckoutPaymentProcessor.objects.create(secret_key="secret", publishable_key="12", name="Stripe")
    service = payment_processor.create_service("stripe", shop=request.shop, tax_class=get_default_tax_class(), enabled=True)
    checkout_phase = StripeCheckoutPhase(request=request, service=service)

    with mock.patch.object(checkout_phase, "get_context_data") as mocked_get_context_data:
        mocked_get_context_data.return_value = {
            "view": checkout_phase,
            "stripe": {
                "publishable_key": "ha",
                "name": "he",
                "description": "hi",
            },
            "customer": contact,
            "stripe_customer_data": {
                "id": "testing",
                "sources": {
                    "data": {
                        "?": True
                    }
                }
            }
        }
        response = checkout_phase.get(request)
        assert response.status_code == 200
        response.render()
        content = response.content.decode("utf-8")
        assert "We use Stripe for secure payment handling. You will only be charged when your order completes" in content
        assert "Click the button below to enter your card details" in content
        assert "Use saved card details by clicking button below" in content

        set_checkout_payment_details_message(shop, "ABC123")
        set_checkout_payment_phase_message(shop, "XYZ987")
        set_checkout_saved_card_message(shop, "QWERTY456")

        response = checkout_phase.get(request)
        assert response.status_code == 200
        response.render()
        content = response.content.decode("utf-8")
        assert "We use Stripe for secure payment handling. You will only be charged when your order completes" not in content
        assert "Click the button below to enter your card details" not in content
        assert "Use saved card details by clicking button below" not in content
        assert "ABC123" in content
        assert "XYZ987" in content
        assert "QWERTY456" in content
