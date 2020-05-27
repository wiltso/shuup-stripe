# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import shuup.apps


class ShuupStripeAppConfig(shuup.apps.AppConfig):
    name = "shuup_stripe"
    label = "shuup_stripe"
    verbose_name = "Shuup Stripe Checkout integration"

    provides = {
        "front_service_checkout_phase_provider": [
            "shuup_stripe.checkout_phase:StripeCheckoutPhaseProvider"
        ],
        "service_provider_admin_form": [
            "shuup_stripe.admin_forms:StripeCheckoutAdminForm"
        ],
        "payment_processor_wizard_form_def": [
            "shuup_stripe.admin_forms:StripeCheckoutWizardFormDef"
        ],
        "stripe_charger": [
            "shuup_stripe.module:StripeCharger"
        ],
        "customer_dashboard_items": [
            "shuup_stripe.dashboard_items:SavedPaymentInfoDashboardItem"
        ],
        "front_urls": [
            "shuup_stripe.urls:urlpatterns"
        ],
        "admin_shop_form_part": [
            "shuup_stripe.admin_module.form_parts.StripeConfigurationFormPart"
        ],
        "admin_module": [
            "shuup_stripe.admin_module:StripeModule",
        ],
        "admin_order_section": [
            "shuup_stripe.order_section:StripePaymentSection"
        ],
        "notify_event": [
            "shuup_stripe.notify_events:SendStripePaymentLink",
        ],
    }
