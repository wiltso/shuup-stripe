# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf.urls import url

from shuup_stripe.views.oauth import stripe_oauth_callback

urlpatterns = [
    url(r'^stripe/connect/$', stripe_oauth_callback, name='stripe_connect_auth'),
]
