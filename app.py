import connexion
import database.db as db
from flask import g
import os

# Create application instance
app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file for endpoints configuration
app.add_api('swagger.yml')

# Create storage connections instance
#storage_connections = StorageConnections('database.db')

@app.app.before_request
def before_request():
    db.connect_to_db('database.db')

@app.app.teardown_request
def teardown_request(exception):
    db.close_db()

if __name__ == '__main__':
    with app.app.app_context():
        db.connect_to_db('database.db')
        connection = db.get_db()
        db.create_tables(connection)

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)




