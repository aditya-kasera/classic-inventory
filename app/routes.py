from app import app
# from flask import render_template


from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    app.logger.info('Home page accessed')
    return render_template('index.html')