import connexion
from flask import g
import os
from database.db_orm_mapping import sqla
import storage.aws_s3 as aws_s3

# Create application instance
app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file for endpoints configuration
app.add_api('swagger.yml')


@app.app.before_first_request
def before_first_request():
    aws_s3.create_bucket()


def clean_up():
    with app.app.app_context():
        sqla.drop_all()
    
    buckets = aws_s3.get_buckets()
    for b in buckets:
        aws_s3.empty_and_delete_bucket(b)

if __name__ == '__main__':
    # Database set up
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    sqla.init_app(app.app)

    with app.app.app_context():
        sqla.create_all()

    try:
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), debug=True)
    finally:
        clean_up()
