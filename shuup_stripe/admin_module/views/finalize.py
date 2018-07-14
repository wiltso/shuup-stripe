# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.http.response import HttpResponseRedirect
from django.views.generic.edit import FormView
from shuup.admin.shop_provider import get_shop
from shuup.core.models import FixedCostBehaviorComponent

from shuup_stripe.admin_module.forms import FinalizeForm
from shuup_stripe.utils import (
    ensure_stripe_method_for_shop, get_payment_method_for_shop,
    get_stripe_oauth_data
)


class StripeFinalizeConnectView(FormView):
    template_name = "shuup/stripe/finalize.jinja"
    form_class = FinalizeForm

    def form_valid(self, form):
        shop = get_shop(self.request)
        stripe_config = get_stripe_oauth_data(shop)
        publishable_key = stripe_config.get("stripe_publishable_key")

        with atomic():
            ensure_stripe_method_for_shop(
                shop,
                publishable_key,
                form.cleaned_data["tax_class"],
                form.cleaned_data["name"],
                form.cleaned_data.get("description", ""),
                form.cleaned_data.get("price", 0),
            )
        return HttpResponseRedirect(reverse("shuup_admin:shuup_stripe.connect"))

    def get_form_kwargs(self):
        kwargs = super(StripeFinalizeConnectView, self).get_form_kwargs()
        payment_method = get_payment_method_for_shop(get_shop(self.request))
        if payment_method:
            component = payment_method.behavior_components.instance_of(FixedCostBehaviorComponent).first()
            kwargs["initial"] = dict(
                name=payment_method.name,
                description=payment_method.description,
                tax_class=payment_method.tax_class,
                price=component.price_value if component else 0
            )
        return kwargs
