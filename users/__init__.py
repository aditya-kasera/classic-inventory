from flask import Blueprint

usersInstance = Blueprint('users', __name__, template_folder='templates')

from users import routes
