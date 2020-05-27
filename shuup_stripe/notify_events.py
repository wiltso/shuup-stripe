# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from shuup.notify.base import Event, Variable
from shuup.notify.typology import Email, Language, Model, URL


class SendStripePaymentLink(Event):
    identifier = "stripe_checkout_payment_link"
    name = _("Send Stripe Payment Link")
    description = _("This event is triggered manually from order.")

    order = Variable(_("Order"), type=Model("shuup.Order"))
    customer_email = Variable(_("Customer Email"), type=Email)
    payment_link = Variable(_("URL to Stripe payment lin"), type=URL)
    language = Variable(_("Language"), type=Language)
