# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django import forms
from django.utils.translation import ugettext_lazy as _
from shuup.admin.forms import ShuupAdminForm
from shuup.admin.forms.widgets import TextEditorWidget
from shuup.admin.modules.service_providers.wizard_form_defs import (
    ServiceWizardFormDef
)
from shuup.admin.modules.service_providers.wizard_forms import (
    ServiceWizardForm
)
from shuup.core.models import TaxClass

from shuup_stripe.models import StripeCheckoutPaymentProcessor


class FinalizeForm(forms.Form):
    name = forms.CharField(max_length=128, label=_("Name"), initial="Stripe", required=True)
    description = forms.CharField(
        max_length=256,
        required=False,
        label=_("Description"),
        initial=_("Make your payment in Stripe payment service."),
        widget=TextEditorWidget
    )
    tax_class = forms.ModelChoiceField(
        label=_("Tax Class"),
        required=True,
        queryset=TaxClass.objects.filter(enabled=True)
    )
    price = forms.DecimalField(
        required=False, min_value=0, initial=0,
        label=_("Price"),
        help_text=_("Price of the service")
    )

    def clean_price(self):
        return self.cleaned_data.get("price", None) or 0


class StripeCheckoutAdminForm(ShuupAdminForm):
    class Meta:
        model = StripeCheckoutPaymentProcessor
        fields = '__all__'
        widgets = {
            'secret_key': forms.PasswordInput(render_value=True),
            'publishable_key': forms.PasswordInput(render_value=True),
        }


class StripeCheckoutWizardForm(ServiceWizardForm):
    class Meta:
        model = StripeCheckoutPaymentProcessor
        fields = ("name", "service_name", "secret_key", "publishable_key")
        widgets = {
            'secret_key': forms.PasswordInput(render_value=True),
            'publishable_key': forms.PasswordInput(render_value=True),
        }

    def __init__(self, **kwargs):
        super(StripeCheckoutWizardForm, self).__init__(**kwargs)
        if not self.provider:
            return
        service = self.get_payment_method()
        if not service:
            return
        self.fields["service_name"].initial = service.name
        self.fields["secret_key"].initial = self.provider.secret_key
        self.fields["publishable_key"].initial = self.provider.publishable_key


class StripeCheckoutWizardFormDef(ServiceWizardFormDef):
    def __init__(self, request):
        super(StripeCheckoutWizardFormDef, self).__init__(
            name="stripe",
            form_class=StripeCheckoutWizardForm,
            template_name="shuup/stripe/wizard_form.jinja",
            request=request
        )
