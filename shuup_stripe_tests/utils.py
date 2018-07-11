# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.shortcuts import redirect
from django.utils.timezone import now
from shuup.testing.factories import (
    create_order_with_product, get_default_product, get_default_supplier,
    get_default_tax_class
)
from shuup.utils.http import retry_request

from shuup_stripe.redirector import StripeRedirector


def create_order_for_stripe(stripe_payment_processor, identifier=None, unit_price=100):
    product = get_default_product()
    supplier = get_default_supplier()
    order = create_order_with_product(
        product=product, supplier=supplier, quantity=1,
        taxless_base_unit_price=unit_price, tax_rate=0
    )
    payment_method = stripe_payment_processor.create_service(
        identifier, shop=order.shop, tax_class=get_default_tax_class(), enabled=True)
    order.payment_method = payment_method
    order.cache_prices()
    assert order.taxless_total_price.value > 0
    if not order.payment_data:
        order.payment_data = {}
    order.save()
    return order


def get_stripe_token(stripe_payment_processor):
    return retry_request(
        method="post",
        url="https://api.stripe.com/v1/tokens",
        auth=(stripe_payment_processor.secret_key, "x"),
        data={
            "card[number]": "4242424242424242",
            "card[exp_month]": 12,
            "card[exp_year]": now().date().year + 1,
            "card[cvc]": 666,
        }
    ).json()


class GoogleRedirector(StripeRedirector):
    def redirect(self, **kwargs):
        return redirect("https://www.google.com")
