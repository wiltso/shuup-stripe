.. image:: https://travis-ci.org/shuup/shuup-stripe.svg?branch=master
    :target: https://travis-ci.org/shuup/shuup-stripe
.. image::
   https://codecov.io/gh/shuup/shuup-stripe/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/shuup/shuup-stripe

Shuup Stripe Addon
==================

This package implements `Stripe Checkout <https://stripe.com/checkout>`__
for the `Shuup <https://shuup.com/>`__ platform.

Copyright
---------

Copyright (C) 2012-2018 by Shuup Inc. <support@shuup.com>

Shuup is International Registered Trademark & Property of Shuup Inc.,
Business Address: 1013 Centre Road, Suite 403-B,
Wilmington, Delaware 19805,
United States Of America

License
-------

Shuup Stripe addon is published under Open Software License version 3.0 (OSL-3.0).
See the LICENSE file distributed with Shuup.

Running tests
-------------

You can run tests with `py.test <http://pytest.org/>`_.

Requirements for running tests:

* Your virtualenv needs to have Shuup installed.

* Project root must be in the Python path.  This can be done with:

  .. code:: sh

     pip install -e .

* The packages from ``requirements-test.txt`` must be installed.

  .. code:: sh

     pip install -r requirements-test.txt

To run tests, use command:

.. code:: sh

   py.test -v

or use preset which builds coverage as well:

.. code:: sh

   npm test
