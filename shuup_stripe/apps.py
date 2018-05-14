# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import shuup.apps


class ShuupStripeAppConfig(shuup.apps.AppConfig):
    name = "shuup_stripe"
    label = "shuup_stripe"
    verbose_name = "Shuup Stripe Checkout integration"

    provides = {
        "front_service_checkout_phase_provider": [
            "shuup_stripe.checkout_phase:StripeCheckoutPhaseProvider",
        ],
        "service_provider_admin_form": [
            "shuup_stripe.admin_forms:StripeCheckoutAdminForm",
        ],
        "payment_processor_wizard_form_def": [
            "shuup_stripe.admin_forms:StripeCheckoutWizardFormDef",
        ],
        "front_urls_pre": [
            "shuup_stripe.urls:urlpatterns"
        ],
        "admin_module": [
            "shuup_stripe.admin_module:StripeAdminModule"
        ]
    }
