import os

class Config(object):
    # WTForms use this key to protect from CSRF attacks
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = 1
 

    GOOGLE_CLIENT_ID = "<unique-key>.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "client_secret"
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
