# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.html import strip_tags
from django_jinja import library
from jinja2.utils import contextfunction

from shuup_stripe.utils import (
    get_checkout_payment_details_message, get_checkout_payment_phase_message,
    get_checkout_saved_card_message, get_saved_card_message
)


class StripeNamespace(object):
    @contextfunction
    def get_saved_card_message(self, context):
        custom_message = get_saved_card_message(context["request"].shop)
        if strip_tags(custom_message).strip():
            return custom_message

    @contextfunction
    def get_checkout_payment_phase_message(self, context):
        custom_message = get_checkout_payment_phase_message(context["request"].shop)
        if strip_tags(custom_message).strip():
            return custom_message

    @contextfunction
    def get_checkout_payment_details_message(self, context):
        custom_message = get_checkout_payment_details_message(context["request"].shop)
        if strip_tags(custom_message).strip():
            return custom_message

    @contextfunction
    def get_checkout_saved_card_message(self, context):
        custom_message = get_checkout_saved_card_message(context["request"].shop)
        if strip_tags(custom_message).strip():
            return custom_message


library.global_function(name="stripe_utils", fn=StripeNamespace())
