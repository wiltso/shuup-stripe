# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import AdminModule
from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.urls import admin_url
from shuup.admin.views.home import SimpleHelpBlock

from shuup_stripe.utils import get_stripe_oauth_data


class StripeAdminModule(AdminModule):
    def get_help_blocks(self, request, kind):
        connected = False
        shop = get_shop(request)
        conf = get_stripe_oauth_data(shop)
        if conf:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            data = stripe.Account.retrieve(conf["stripe_user_id"])
            connected = (data and data["id"] == conf["stripe_user_id"])

        if kind == "setup":
            actions = [
                {
                    "text": _("Re-connect Stripe") if connected else _("Connect Stripe"),
                    "url": reverse_lazy("shuup_admin:shuup_stripe.connect"),
                }
            ]

            if connected:
                actions.append({
                    "text": _("Edit connection"),
                    "url": reverse_lazy("shuup_admin:shuup_stripe.finalize"),
                })

            yield SimpleHelpBlock(
                priority=0.1,  # not the first but pretty high...
                text=_("Stripe"),
                description_html=True,
                description=_("Connect your Stripe account to Shuup store. "
                              "Once connected, you are able to receive payments."),
                actions=actions,
                icon_url="stripe/stripe_blue.svg",
                done=connected,
            )

    def get_urls(self):
        return [
            admin_url(
                "^stripe/connect/$",
                "shuup_stripe.admin_module.views.StripeConnectView",
                name="shuup_stripe.connect"
            ),
            admin_url(
                "^stripe/finalize/$",
                "shuup_stripe.admin_module.views.StripeFinalizeConnectView",
                name="shuup_stripe.finalize"
            )
        ]
