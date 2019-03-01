# -*- coding: utf-8 -*-
# This file is part of Shuup Stripe Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from shuup.front.utils.dashboard import DashboardItem


class SavedPaymentInfoDashboardItem(DashboardItem):
    title = _("Saved Card")
    icon = "fa fa-credit-card"
    _url = "shuup:stripe_saved_payment"

    def show_on_menu(self):
        return True

    def show_on_dashboard(self):
        return False
