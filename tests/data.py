# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
CUSTOMER_CREATE_DATA = {
    "id": "cus_CpxrKhREwRfFHu",
    "object": "customer",
    "account_balance": 0,
    "created": 1525970862,
    "currency": "cad",
    "default_source": None,
    "delinquent": False,
    "description": None,
    "discount": None,
    "email": None,
    "invoice_prefix": "902950F",
    "livemode": False,
    "metadata": {},
    "shipping": None,
    "sources": {
        "object": "list",
        "data": [],
        "has_more": False,
        "total_count": 0,
        "url": "/v1/customers/cus_CpxrKhREwRfFHu/sources"
    },
    "subscriptions": {
        "object": "list",
        "data": [],
        "has_more": False,
        "total_count": 0,
        "url": "/v1/customers/cus_CpxrKhREwRfFHu/subscriptions"
    }
}

CHARGE_CREATE_DATA = {
    "id": "ch_1CQHveKujtwwujKtZokw7zrn",
    "object": "charge",
    "amount": 100,
    "amount_refunded": 0,
    "application": None,
    "application_fee": None,
    "balance_transaction": "txn_1CPypMKujtwwujKtdCgD33cf",
    "captured": False,
    "created": 1525970862,
    "currency": "cad",
    "customer": None,
    "description": "My First Test Charge (created for API docs)",
    "destination": None,
    "dispute": None,
    "failure_code": None,
    "failure_message": None,
    "fraud_details": {},
    "invoice": None,
    "livemode": False,
    "metadata": {},
    "on_behalf_of": None,
    "order": None,
    "outcome": None,
    "paid": True,
    "receipt_email": None,
    "receipt_number": None,
    "refunded": False,
    "refunds": {
        "object": "list",
        "data": [],
        "has_more": False,
        "total_count": 0,
        "url": "/v1/charges/ch_1CQHveKujtwwujKtZokw7zrn/refunds"
    },
    "review": None,
    "shipping": None,
    "source": {
        "id": "card_1CPyxgKujtwwujKtkoOOGJgM",
        "object": "card",
        "address_city": None,
        "address_country": None,
        "address_line1": None,
        "address_line1_check": None,
        "address_line2": None,
        "address_state": None,
        "address_zip": None,
        "address_zip_check": None,
        "brand": "Visa",
        "country": "US",
        "customer": "cus_CpeGds7hA3jJxZ",
        "cvc_check": "pass",
        "dynamic_last4": None,
        "exp_month": 12,
        "exp_year": 2019,
        "fingerprint": "JtGJTPeq8NwDlIji",
        "funding": "credit",
        "last4": "4242",
        "metadata": {},
        "name": "asdf@ee.com",
        "tokenization_method": None
    },
    "source_transfer": None,
    "statement_descriptor": None,
    "status": "succeeded",
    "transfer_group": None
}


TOKEN_RETRIEVE_DATA = {
    "id": "tok_1CPwPtKujtwwujKtZNfPWQCc",
    "object": "token",
    "card": {
        "id": "card_1CPwPtKujtwwujKtXdLVCTXS",
        "object": "card",
        "address_city": None,
        "address_country": None,
        "address_line1": None,
        "address_line1_check": None,
        "address_line2": None,
        "address_state": None,
        "address_zip": None,
        "address_zip_check": None,
        "brand": "Visa",
        "country": "US",
        "cvc_check": None,
        "dynamic_last4": None,
        "exp_month": 8,
        "exp_year": 2019,
        "fingerprint": "JtGJTPeq8NwDlIji",
        "funding": "credit",
        "last4": "4242",
        "metadata": {},
        "name": None,
        "tokenization_method": None
    },
    "client_ip": None,
    "created": 1525888169,
    "livemode": False,
    "type": "card",
    "used": False
}
