import logging
import os
from flask_mysqldb import MySQL
from flask import Flask

def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='../static', template_folder='templates')
    app.secret_key = 'a loooooooongggg stringgggggggggg'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'grassroot'
    app.config['MYSQL_DB'] = 'IMS'
    
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application instance created')
    return app

def initialize_extensions(app):
    app.logger.info('Database connected')
    mysql = MySQL(app)
    return mysql

