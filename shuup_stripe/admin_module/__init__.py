# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import json

import stripe
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from shuup import configuration
from shuup.admin.base import AdminModule
from shuup.admin.utils.urls import admin_url
from shuup.admin.views.home import SimpleHelpBlock


class StripeAdminModule(AdminModule):
    def get_dashboard_blocks(self, request):
        return []

    def get_required_permissions(self):
        return ()

    def get_help_blocks(self, request, kind):
        connected = False
        conf = json.loads(configuration.get(request.shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        if conf:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            data = stripe.Account.retrieve(conf["stripe_user_id"])
            connected = (data and data["id"] == conf["stripe_user_id"])
        if kind == "setup":
            yield SimpleHelpBlock(
                priority=0.1,  # not the first but pretty high...
                text=_("Stripe"),
                description_html=True,
                description=_("Connect your Stripe account to Shuup store. "
                              "Once connected, you are able to receive payments."),
                actions=[{
                    "text": _("Connect Stripe"),
                    "url": reverse_lazy("shuup_admin:shuup_stripe.connect"),
                }],
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
        ]
