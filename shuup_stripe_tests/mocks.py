# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from .data import CHARGE_CREATE_DATA, CUSTOMER_CREATE_DATA, TOKEN_RETRIEVE_DATA


class StripedData(dict):
    def __getattr__(self, attr):
        return self[attr]

    def json(self):
        return self


def mock_get_stripe_oauth_token(payload):
    return {
        "access_token": "adf",
        "scope": "read_write",
        "livemode": False,
        "token_type": "bearer",
        "refresh_token": "rt_test_derp123",
        "stripe_user_id": "sk_test_adfadsfadf",
        "stripe_publishable_key": "pk_test_asdfadsf",
    }


def mock_customer_create(**kwargs):
    return StripedData(**CUSTOMER_CREATE_DATA)


def mock_token_retrieve(token, **kwargs):
    return StripedData(**TOKEN_RETRIEVE_DATA)


def mock_charge_create(**kwargs):
    return StripedData(**CHARGE_CREATE_DATA)
