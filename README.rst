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

Copyright (c) 2012-2018 by Shoop Commerce Ltd. <contact@shuup.com>

Shuup is International Registered Trademark & Property of Shoop Commerce Ltd.,
Business ID: FI24815722, Business Address: Aurakatu 12 B, 20100 Turku,
Finland.

License
-------

Shuup Stripe Addon is published under the GNU Affero General Public License,
version 3 (AGPLv3). See the LICENSE file.

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
