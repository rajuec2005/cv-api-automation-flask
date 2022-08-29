from mongoengine import *
import mongoengine_goodjson as gj
from main.utils.constants import *





class Apis(gj.Document):
    api_name = StringField(required=True)
    api_desc = StringField(required=True)
    service_name = StringField(required=True)
    http_method = StringField(required=True, choices=HTTP_METHODS)
    uri = StringField(required=True)