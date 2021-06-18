from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from logging.handlers import SMTPHandler
from oauthlib.oauth2 import WebApplicationClient

application = Flask(__name__)
# to tell flask to read and apply config key
application.config.from_object(Config)
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

login = LoginManager(application)
login.login_view = 'login'

mail = Mail(application)

# import at bottom to avoid flask circular imports
from app import routes