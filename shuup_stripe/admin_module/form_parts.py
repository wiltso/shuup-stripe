# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.forms.widgets import TextEditorWidget

from shuup_stripe.utils import (
    get_checkout_payment_details_message, get_checkout_payment_phase_message,
    get_checkout_saved_card_message, get_saved_card_message,
    set_checkout_payment_details_message, set_checkout_payment_phase_message,
    set_checkout_saved_card_message, set_saved_card_message
)


class StripeConfigurationForm(forms.Form):
    checkout_payment_phase_message = forms.CharField(
        label=_("Checkout payment phase message"),
        help_text=_("Set a custom message to use in checkout payment phase."),
        widget=TextEditorWidget(),
        required=False
    )
    checkout_payment_details_message = forms.CharField(
        label=_("Checkout card details message"),
        help_text=_("Set a custom message to use in card details option when doing checkout."),
        widget=TextEditorWidget(),
        required=False
    )
    checkout_saved_card_message = forms.CharField(
        label=_("Checkout saved card message"),
        help_text=_("Set a custom message to use in saved card option when doing checkout."),
        widget=TextEditorWidget(),
        required=False
    )
    saved_card_message = forms.CharField(
        label=_("Saved card message"),
        help_text=_("Set a custom message for the saved card section in customer dashboard."),
        widget=TextEditorWidget(),
        required=False
    )


class StripeConfigurationFormPart(FormPart):
    priority = 10
    name = "stripe_configuration"
    form = StripeConfigurationForm

    def get_form_defs(self):
        initial = {}
        if self.object.pk:
            initial = {
                "checkout_payment_phase_message": get_checkout_payment_phase_message(self.object),
                "checkout_payment_details_message": get_checkout_payment_details_message(self.object),
                "checkout_saved_card_message": get_checkout_saved_card_message(self.object),
                "saved_card_message": get_saved_card_message(self.object),
            }

        yield TemplatedFormDef(
            name=self.name,
            form_class=self.form,
            template_name="shuup/stripe/shop_form_part.jinja",
            required=False,
            kwargs={"initial": initial}
        )

    def form_valid(self, form):
        vendor_form = form[self.name]

        if vendor_form.has_changed():
            checkout_payment_phase_message = vendor_form.cleaned_data["checkout_payment_phase_message"]
            checkout_payment_details_message = vendor_form.cleaned_data["checkout_payment_details_message"]
            checkout_saved_card_message = vendor_form.cleaned_data["checkout_saved_card_message"]
            saved_card_message = vendor_form.cleaned_data["saved_card_message"]
            set_checkout_payment_phase_message(self.object, checkout_payment_phase_message)
            set_checkout_payment_details_message(self.object, checkout_payment_details_message)
            set_checkout_saved_card_message(self.object, checkout_saved_card_message)
            set_saved_card_message(self.object, saved_card_message)
