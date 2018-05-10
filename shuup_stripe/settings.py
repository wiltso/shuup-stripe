import environ

env = environ.Env(DEBUG=(bool, False))

# This is being used the pull connect data from configuration
STRIPE_CONNECT_OAUTH_DATA_KEY = "stripe_connect_oauth_data"

# platform level secrets for connect to use
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default=None)
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default=None)
STRIPE_CONNECT_REDIRECT_URI = env('STRIPE_CONNECT_REDIRECT_URI', default=None)
STRIPE_CONNECT_REDIRECT_ADMIN_URI = env('STRIPE_CONNECT_REDIRECT_ADMIN_URI', default=None)
STRIPE_OAUTH_CLIENT_ID = env('STRIPE_OAUTH_CLIENT_ID', default=None)

STRIPE_CONNECT_FEE_PERCENTAGE = env('STRIPE_CONNECT_FEE_PERCENTAGE', default=None)

STRIPE_OAUTH_REDIRECTOR = "shuup_stripe.redirector:StripeRedirector"
