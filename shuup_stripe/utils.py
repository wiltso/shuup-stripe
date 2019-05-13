# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from shuup import configuration
from shuup.utils.importing import cached_load

from shuup_stripe.models import StripeCheckoutPaymentProcessor

ZERO_DECIMAL_CURRENCIES = (
    # https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
    "BIF", "CLP", "DJF", "GNF", "JPY", "KMF", "KRW", "MGA",
    "PYG", "RWF", "VND", "VUV", "XAF", "XOF", "XPF"
)


def get_amount_info(amount):
    multiplier = (1 if amount.currency in ZERO_DECIMAL_CURRENCIES else 100)
    return {
        "currency": amount.currency,
        "amount": int(amount.value * multiplier),
    }


def get_stripe_processor(request):
    stripe_processor_provider = cached_load("SHUUP_STRIPE_PROCESSOR_PROVIDER")
    return stripe_processor_provider.get_stripe_processor(request)


class DefaultStripeProcessorProvider(object):
    """
    Returns the first enabled payment processor
    """
    @classmethod
    def get_stripe_processor(cls, request):
        return StripeCheckoutPaymentProcessor.objects.filter(enabled=True).first()


def set_checkout_payment_phase_message(shop, message):
    configuration.set(shop, "stripe_checkout_payment_phase_message", message)


def get_checkout_payment_phase_message(shop):
    return configuration.get(shop, "stripe_checkout_payment_phase_message")


def set_saved_card_message(shop, message):
    configuration.set(shop, "stripe_saved_card_message", message)


def get_saved_card_message(shop):
    return configuration.get(shop, "stripe_saved_card_message")


def set_checkout_payment_details_message(shop, message):
    configuration.set(shop, "stripe_checkout_payment_details_message", message)


def get_checkout_payment_details_message(shop):
    return configuration.get(shop, "stripe_checkout_payment_details_message")


def set_checkout_saved_card_message(shop, message):
    configuration.set(shop, "stripe_checkout_saved_card_message", message)


def get_checkout_saved_card_message(shop):
    return configuration.get(shop, "stripe_checkout_saved_card_message")


def set_checkout_phase_title(shop, title):
    configuration.set(shop, "stripe_checkout_phase_title", title)


def get_checkout_phase_title(shop):
    return configuration.get(shop, "stripe_checkout_phase_title")
