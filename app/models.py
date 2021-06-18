from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login, application
from app.database import database
from time import time
import jwt
# ...

class User(UserMixin):
    def __init__(self, username, validity, MAC):
        self.username = username
        self.validity = validity
        self.MAC = MAC

    def get_id(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, username, password):
        db = database()
        get_password_hash = db.get_password_hash(username)
        if check_password_hash(get_password_hash, password):
            return True
        else:
            return False

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.username, 'exp': time() + expires_in},
            application.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, application.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(username):
    db= database()
    u = db.query_email(username)
    if not u:
        return None
    user_details = db.fetch_user(username)
    return User(username=username, validity=user_details.get('Validity'), MAC=user_details.get('MAC'))