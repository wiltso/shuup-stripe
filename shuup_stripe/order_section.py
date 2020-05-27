# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import Section

from shuup_stripe.models import StripeCheckoutPaymentProcessor


class StripePaymentSection(Section):
    identifier = "stripe_payment_section"
    name = _("Stripe Payment")
    icon = "fa-money"
    template = "shuup/stripe/order_section.jinja"
    order = 2

    @classmethod
    def visible_for_object(cls, obj, request=None):
        if not obj.payment_method:
            return False

        if obj.is_paid():
            return False

        proseccor = obj.payment_method.payment_processor
        return isinstance(proseccor, StripeCheckoutPaymentProcessor)

    @classmethod
    def get_context_data(cls, obj, request=None):
        return {"order": obj}
