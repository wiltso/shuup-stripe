# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect


class StripeRedirector(object):
    def __init__(self, shop):
        self.shop = shop

    def redirect(self, **kwargs):
        if hasattr(settings, "STRIPE_CONNECT_REDIRECT_ADMIN_URI") and settings.STRIPE_CONNECT_REDIRECT_ADMIN_URI:
            redirect_url = settings.STRIPE_CONNECT_REDIRECT_ADMIN_URI
        else:
            redirect_url = reverse_lazy("shuup_admin:shuup_stripe.connect")
        return redirect(redirect_url)
