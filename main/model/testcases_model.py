import mongoengine as me
from mongoengine import *
import mongoengine_goodjson as gj


class URIParams(EmbeddedDocument):
    name = StringField(min_length=1)
    value = StringField(min_length=1)


class PayloadParams(EmbeddedDocument):
    name = StringField(min_length=1)
    value = StringField(min_length=1)


class HTTPResponseBody(EmbeddedDocument):
    json_path = StringField(min_length=1)
    value = StringField(min_length=1)


class Validation(EmbeddedDocument):
    http_status_code = StringField(min_length=1)
    http_response_message = StringField(min_length=1)
    http_response_body = ListField(EmbeddedDocumentField(HTTPResponseBody))


class URIParams(EmbeddedDocument):
    api_reference = BooleanField(required=True)
    name = StringField(required=True, min_length=1)
    value = StringField(required=True, min_length=1)
    tc_name = StringField(min_length=1)


class TestCase(Document):
    tc_id = StringField(required=False)
    tc_name = StringField(required=True, min_length=1)
    tc_desc = StringField()
    service_name = StringField(required=True, min_length=1)
    api_name = StringField(required=True, min_length=1)
    disable = BooleanField(required=True, default=False)
    retry = BooleanField()
    retrycount = IntField()
    uri_params = ListField(EmbeddedDocumentField(URIParams))
    request_payload = DictField()
    validation = ListField(EmbeddedDocumentField(Validation), max_length=1,required=True)