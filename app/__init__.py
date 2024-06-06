from app.connection import create_app, initialize_extensions

app = create_app() #"dev"
mysql = initialize_extensions(app)

# from app import routes
from . import routes        
app.register_blueprint(routes.bp)

from inventory import inventoryInstance
app.register_blueprint(inventoryInstance)
# , url_prefix='/inventory' (for better code)

from users import usersInstance
app.register_blueprint(usersInstance)


app.logger.info('Application startup completed')

