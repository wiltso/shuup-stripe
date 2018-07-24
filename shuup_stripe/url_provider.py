# -*- coding: utf-8 -*-
# This file is part of Shuup Checkout.fi Connect Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.urlresolvers import reverse


class StripeURLProvider(object):
    def get_oauth_callback_url(self, request, shop):
        return request.build_absolute_uri(reverse("shuup:stripe_connect_auth"))

    def get_oauth_finalize_url(self, request, shop):
        return request.build_absolute_uri(reverse("shuup_admin:shuup_stripe.finalize"))
