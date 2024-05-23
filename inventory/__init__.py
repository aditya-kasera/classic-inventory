from flask import Blueprint

inventoryInstance = Blueprint('inventory', __name__, template_folder='templates')

from inventory import routes

