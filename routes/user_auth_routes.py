from flask import Blueprint

user_auth = Blueprint('user_auth', __name__)

@user_auth.route('/register')
def create_explore_feed():
    #TODO
    return "register account"

@user_auth.route('/login')
def create_following_feed():
    #TODO
    return "login"