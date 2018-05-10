import environ

env = environ.Env(DEBUG=(bool, False))

# platform level secrets for connect to use
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default=None)
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default=None)
