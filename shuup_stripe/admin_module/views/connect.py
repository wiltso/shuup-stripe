# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import json

import stripe
from django.conf import settings
from django.views.generic import TemplateView
from shuup import configuration

from shuup_stripe.utils import (
    ensure_stripe_method_for_shop, get_stripe_connect_url
)


class StripeConnectView(TemplateView):
    template_name = "shuup/stripe/connect.jinja"

    def get_context_data(self, **kwargs):
        context = super(StripeConnectView, self).get_context_data(**kwargs)
        shop = self.request.shop
        conf = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        context["connected"] = False
        context["payment_method"] = None
        context["stripe_connect_url"] = get_stripe_connect_url(shop)
        if conf:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            data = stripe.Account.retrieve(conf["stripe_user_id"])
            context["connected"] = (data and data["id"] == conf["stripe_user_id"])
            pm = ensure_stripe_method_for_shop(shop, conf["stripe_publishable_key"])
            context["payment_method"] = pm
            context["payment_method_active"] = (pm and pm.enabled)
        return context
