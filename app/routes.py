from flask import render_template, flash, redirect,  url_for, request
from app import application, client
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.email import send_password_reset_email
from werkzeug.urls import url_parse
from app.database import database
import requests, json
from config import Config

'''
 The view function
 This means that when a web browser requests either of these two URLs, 
 Flask is going to invoke this function and pass the return value of it back to the browser as a response.
'''

def get_google_provider_cfg():
    return requests.get("https://accounts.google.com/.well-known/openid-configuration").json()


@application.route('/')
@application.route('/index')
def index():


    '''
    This function takes a template filename and a variable list of template arguments
    and returns the same template, but with all the placeholders in it replaced with actual values.
    The render_template() function invokes the Jinja2 template engine that comes bundled with the Flask framework.
    Jinja2 substitutes {{ ... }} blocks with the corresponding values,
    given by the arguments provided in the render_template() call.
    '''
    return render_template('index.html', title='Empower')

@application.route('/documentation')
def documentation():
    return render_template('documentation.html', title='Empower')

@application.route('/downloads')
def downloads():
    return render_template('downloads.html', title='Empower')

@application.route('/about')
def about():
    return render_template('about.html', title='Empower')

@application.route('/myaccount', methods=['GET', 'POST'])
@login_required
def loggedIn():

    form = LoginForm()
    return render_template('myaccount.html', title='Empower-LoggedIn', form=form, email=request.args.get('email'),
                           validity=request.args.get('validity'),MAC=request.args.get('MAC'))

# # methods tell flask that this view func accepts get and post request
@application.route('/login', methods=['GET', 'POST'])
def login():  
    if current_user.is_authenticated:
        return redirect(url_for('loggedIn'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        if user.check_password(form.username.data, form.password.data):
            # current_user.is_authenticated = True
            # current_user.is_anonymus = False
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('loggedIn'))
        else:
            flash('Invalid Password!')
    return render_template('login.html', title='Empower-Sign In', form=form)

@application.route('/login_google', methods=['GET', 'POST'])
def login_google():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid","email"],
    )
    return redirect(request_uri)

@application.route("/login_google/callback")
def callback():
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    # Get authorization code Google sent back to you

    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # Parse the tokens!
    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        db = database()
        email_exists = db.query_email(users_email)
        if email_exists:
            # get user data and redirect
            user_details = db.fetch_user(users_email)
            user = User(username=users_email, validity=user_details.get('Validity'), MAC = user_details.get('MAC'))
            login_user(user)
            return redirect(url_for('loggedIn', email=user.username, validity=user.validity,
                                    MAC = user.MAC))

        else:
            db.register(users_email)
            user = User(username=users_email, validity='None', MAC = '000')
            login_user(user)
            return redirect(url_for('loggedIn', email=user.username, validity=user.validity,
                                    MAC=user.MAC))

@application.route('/signup', methods=['GET', 'POST'])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for('loggedIn'))
    regform = RegistrationForm()
    if regform.validate_on_submit():
        db = database()
        user = User(username=regform.username.data)
        user.set_password(regform.password.data)
        db.register(user.username,user.password_hash)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Empower-Sign In', form=regform)


@application.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))

@application.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User(username=form.email.data)
        # if user:
        send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@application.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        # db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)