from flask_mail import Message
from app import mail, application
from threading import Thread
from flask import render_template

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(application, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password',
               sender='sender@gmail.com',
               recipients=[user.username],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_async_email(app, msg):
    with app.app_context():
        mail.connect()
        mail.send(msg)
