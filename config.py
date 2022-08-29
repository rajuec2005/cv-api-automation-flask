"""[General Configuration Params]
"""
from os import environ, path

basedir = path.abspath(path.dirname(__file__))
Token_URL = "https://cloudgateway.trusted.visa.com:8443/cloudgateway/security/tokens"
Token_PAYLOAD = {'username': 'svclqa', 'password': '1+S*61%d#V*nu9Q'}
PORT = "8443"
SR_HOSTNAME = "sl73cvamsapd068"

SENDER_ADDR = "svcatlus_dev@visa.com"
PASSWORD = "3KPJ24XjuYe8zqWf"
RECEIVER_ADDR = []
EMAIL_HOST = 'corpportal.visa.com'
EMAIL_PORT = 25



class Config(object):
    DEBUG = True
    DB_NAME = "flask_db_stage"
    DB_URI = "localhost"
    DB_PORT = 27017
    # MONGODB_SETTINGS = {
    #     'db': 'flask_db',
    #     'host': 'localhost',
    #     'port': 27017
    # }


class ProdConfig(Config):
    pass


class UATConfig(Config):
    DEBUG = True


class StageConfig(Config):
    DB_NAME = "flask_db"


class localConfig(Config):
    pass