# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import json

from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.generic import View
from shuup import configuration
from shuup.core.models import Shop
from shuup.utils.importing import load

from shuup_stripe.utils import (
    ensure_stripe_method_for_shop, ensure_stripe_token)


class OAuthCallbackView(View):
    redirect_provider_key = "shuup_stripe_redirect_provider"
    """
    View for Stripe OAuth Callback

    Apart from basic validation, it will retrieve
    the user account information.

    Once the information has been fetched, the
    user is being redirected to admin.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.method != "GET":
            return HttpResponseBadRequest("invalid request")
        if "state" not in request.GET:
            return HttpResponseBadRequest("invalid request")
        if "code" not in request.GET:
            return HttpResponseBadRequest("invalid request")
        authorization_code = request.GET["code"]
        # do auth
        try:
            shop_id = int(request.GET["state"].split("_")[2])
            shop = Shop.objects.get(id=shop_id)
        except (IndexError, Shop.DoesNotExist):
            return HttpResponseBadRequest("invalid request")

        ensure_stripe_token(shop, authorization_code)
        conf = json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))
        if conf:
            ensure_stripe_method_for_shop(shop, conf["stripe_publishable_key"])

        rd = load(settings.STRIPE_OAUTH_REDIRECTOR)
        redirector = rd(shop)
        return redirector.redirect()
