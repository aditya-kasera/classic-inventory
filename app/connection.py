from flask_mysqldb import MySQL
from flask import Flask

def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='../static', template_folder='templates')
    app.secret_key = 'a loooooooongggg stringgggggggggg'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'grassroot'
    app.config['MYSQL_DB'] = 'IMS'
    return app

def initialize_extensions(app):
    mysql = MySQL(app)
    return mysql