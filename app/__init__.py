from app.connection import create_app, initialize_extensions

app = create_app()
mysql = initialize_extensions(app)

# from app import routes
from app import routes 

from inventory import inventoryInstance
app.register_blueprint(inventoryInstance)
# , url_prefix='/inventory' (better code)

from users import usersInstance
app.register_blueprint(usersInstance)



