from flask import Blueprint

user_auth = Blueprint('user_auth', __name__)

@user_auth.route('/login')
def login():
    #TODO
    return "login"