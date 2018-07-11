# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import pytest

from django.test import override_settings

from shuup.admin.views.wizard import WizardView
from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware


@pytest.mark.django_db
def test_wizard_pane(rf, admin_user, settings):
    with override_settings(SHUUP_SETUP_WIZARD_PANE_SPEC=["shuup.admin.modules.service_providers.views.PaymentWizardPane"]):
        factories.get_default_shop()
        factories.get_default_tax_class()

        request = apply_request_middleware(rf.get("/"), user=admin_user)
        response = WizardView.as_view()(request)
        assert response.status_code == 200
