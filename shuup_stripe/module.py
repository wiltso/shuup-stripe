# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import json

import stripe
from django.conf import settings
from django.utils.translation import ugettext as _
from shuup import configuration
from shuup.utils.excs import Problem
from shuup.utils.http import retry_request

from shuup_stripe.utils import (
    add_fee_to_payload, ensure_stripe_token, get_amount_info)


def _handle_stripe_error(charge_data):
    error_dict = charge_data.get("error")
    if error_dict:
        raise Problem("Stripe: %(message)s (%(type)s)" % error_dict)
    failure_code = charge_data.get("failure_code")
    failure_message = charge_data.get("failure_message")
    if failure_code or failure_message:
        raise Problem(
            "Stripe: %(failure_message)s (%(failure_code)s)" % charge_data
        )


class StripeCharger(object):
    def __init__(self, secret_key, order):
        self.secret_key = secret_key
        self.order = order

    def _send_request(self):
        stripe_token = self.order.payment_data["stripe"]["token"]
        input_data = {
            "source": stripe_token,
            "description": _("Payment for order {id} on {shop}").format(
                id=self.order.identifier, shop=self.order.shop,
            ),
        }
        input_data.update(get_amount_info(self.order.taxful_total_price))

        if self.order.payment_method.choice_identifier == "stripe_connect":
            input_data["headers"] = {
                "Idempotency-Key": self.order.key,
                "Stripe-Version": "2015-04-07"
            }
            return self._stripe_connect_charge(input_data)

        return retry_request(
            method="post",
            url="https://api.stripe.com/v1/charges",
            data=input_data,
            auth=(self.secret_key, "x"),
            headers={
                "Idempotency-Key": self.order.key,
                "Stripe-Version": "2015-04-07"
            }
        )

    def refresh_token(self):
        shop = self.order.shop
        ensure_stripe_token(shop)
        return json.loads(configuration.get(shop, settings.STRIPE_CONNECT_OAUTH_DATA_KEY, "{}"))

    def _stripe_connect_charge(self, input_data):
        stripe.api_key = self.secret_key

        # ensure Oauth Token is up to date
        stripe_payload = self.refresh_token()
        connect_access_token = stripe_payload['access_token']

        # create customer
        card_info = self.order.payment_data["stripe"]
        customer_token = stripe.Token.retrieve(card_info["token"])
        connect_customer = stripe.Customer.create(
            card=customer_token.id,
            email=card_info["email"],
            api_key=connect_access_token
        )

        # refresh token and charge card
        stripe_payload = self.refresh_token()
        connect_access_token = stripe_payload['access_token']

        payload = dict(
            amount=input_data["amount"],
            currency=input_data["currency"],
            customer=connect_customer.id,
            description=input_data["description"],
            api_key=connect_access_token
        )

        add_fee_to_payload(self.order, payload)

        return stripe.Charge.create(**payload)

    def create_charge(self):
        resp = self._send_request()
        charge_data = resp.json() if hasattr(resp, "json") else resp
        _handle_stripe_error(charge_data)
        if not charge_data.get("paid"):
            raise Problem("Stripe Charge does not say 'paid'")

        return self.order.create_payment(
            self.order.taxful_total_price,
            payment_identifier="Stripe-%s" % charge_data["id"],
            description="Stripe Charge"
        )
