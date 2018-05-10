# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf.urls import url

from shuup_stripe.views import OAuthCallbackView

urlpatterns = [
    url(r'^stripe/connect/$', OAuthCallbackView.as_view(), name='stripe_connect_auth'),
]
