# from flask_mongoengine import MongoEngine
from mongoengine import connect


def initialize_db(dbname, uri, port):
    connect(dbname, host='localhost', port=port)
    # connect(dbname, host, port)