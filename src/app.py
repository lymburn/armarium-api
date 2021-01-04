import connexion
#from database.StorageConnections import StorageConnections
from database.db import connect_to_db, close_db
from flask import g

# Create application instance
app = connexion.App(__name__, specification_dir='./api')

# Read the swagger.yml file for endpoints configuration
app.add_api('swagger.yml')

# Create storage connections instance
#storage_connections = StorageConnections('database.db')

@app.app.before_request
def before_request():
    connect_to_db('database.db')

@app.app.teardown_request
def teardown_request(exception):
    close_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


