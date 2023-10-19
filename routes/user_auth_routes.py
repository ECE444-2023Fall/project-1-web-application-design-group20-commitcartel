from flask import Blueprint

user_auth = Blueprint('user_auth', __name__)

@user_auth.route('/register', method = ['POST'])
def register_user():
    #TODO
    return "register account"

@user_auth.route('/login')
def login():
    #TODO
    return "login"