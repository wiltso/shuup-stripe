# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from shuup.core.models import Shop

from shuup_stripe.utils import decode_state, ensure_stripe_token


def stripe_oauth_callback(request):
    """
    View for Stripe OAuth Callback

    Apart from basic validation, it will retrieve
    the user account information.

    Once the information has been fetched, the
    user is being redirected to admin.
    """
    if request.method != "GET":
        return HttpResponseBadRequest("invalid request")
    if "state" not in request.GET:
        return HttpResponseBadRequest("invalid request")
    if "code" not in request.GET:
        return HttpResponseBadRequest("invalid request")

    authorization_code = request.GET["code"]

    state = decode_state(request.GET["state"])
    if not state:
        return HttpResponseBadRequest("invalid state")

    try:
        shop = Shop.objects.get(id=state["shop"])
        ensure_stripe_token(shop, authorization_code)
        return HttpResponseRedirect("{}?auth_code={}".format(state["finalize_url"], authorization_code))

    except (KeyError, Shop.DoesNotExist):
        return HttpResponseBadRequest("invalid request")
