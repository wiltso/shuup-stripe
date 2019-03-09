# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from shuup.core import cache
from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware

from shuup_stripe.admin_module.form_parts import StripeConfigurationFormPart
from shuup_stripe.utils import (
    get_checkout_payment_details_message, get_checkout_payment_phase_message,
    get_checkout_saved_card_message, get_saved_card_message
)


@pytest.mark.django_db
def test_shop_form_part(rf):
    cache.clear()
    shop = factories.get_default_shop()
    request = apply_request_middleware(rf.get("/"))

    # nothing changed
    form_part = StripeConfigurationFormPart(request, shop)
    form = list(form_part.get_form_defs())[0].instantiate(prefix="stripe")
    assert form.has_changed() is False
    assert not get_checkout_payment_details_message(shop)
    assert not get_checkout_payment_phase_message(shop)
    assert not get_checkout_saved_card_message(shop)
    assert not get_saved_card_message(shop)

    request = apply_request_middleware(rf.post("/"))
    data = {
        "stripe-checkout_payment_details_message": "A",
        "stripe-checkout_payment_phase_message": "B",
        "stripe-checkout_saved_card_message": "C",
        "stripe-saved_card_message": "D"
    }
    form_part = StripeConfigurationFormPart(request, shop)
    form = list(form_part.get_form_defs())[0].instantiate(prefix="stripe", data=data)
    assert form.is_valid()
    form_part.form_valid({StripeConfigurationFormPart.name: form})
    assert get_checkout_payment_details_message(shop) == "A"
    assert get_checkout_payment_phase_message(shop) == "B"
    assert get_checkout_saved_card_message(shop) == "C"
    assert get_saved_card_message(shop) == "D"
