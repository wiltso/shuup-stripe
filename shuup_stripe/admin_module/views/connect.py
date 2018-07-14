# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf import settings
from django.views.generic import TemplateView
from shuup.admin.shop_provider import get_shop
from shuup.utils.importing import load

from shuup_stripe.utils import (
    get_payment_method_for_shop, get_stripe_connect_url, get_stripe_oauth_data
)


class StripeConnectView(TemplateView):
    template_name = "shuup/stripe/connect.jinja"

    def get_context_data(self, **kwargs):
        context = super(StripeConnectView, self).get_context_data(**kwargs)
        shop = get_shop(self.request)
        conf = get_stripe_oauth_data(shop)
        stripe_url_provider = load(settings.STRIPE_URL_PROVIDER)()

        context["connected"] = False
        context["payment_method"] = get_payment_method_for_shop(shop)
        finalize_url = stripe_url_provider.get_oauth_finalize_url(self.request, shop)
        context["stripe_connect_url"] = get_stripe_connect_url(self.request, shop)
        context["finalize_url"] = finalize_url

        if conf:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            data = stripe.Account.retrieve(conf["stripe_user_id"])
            context["connected"] = (data and data["id"] == conf["stripe_user_id"])

        return context
