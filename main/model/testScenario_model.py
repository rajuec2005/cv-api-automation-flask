# from .db import db
import mongoengine as me
from mongoengine import EmbeddedDocument, EmbeddedDocumentListField, Document, EmbeddedDocumentField
import mongoengine_goodjson as gj


class OutputVariables(EmbeddedDocument):
    name = me.StringField()
    Value = me.StringField()


class InputVariables(EmbeddedDocument):
    name = me.StringField()
    Value = me.StringField()


class TestCases(EmbeddedDocument):
    tc_name = me.StringField()
    # output_variables = me.ListField(EmbeddedDocumentField(OutputVariables))
    # input_variables = me.ListField(EmbeddedDocumentField(InputVariables))


class TestScenario(gj.Document):
    service_name = me.StringField(required=True)
    groups = me.ListField(required=True)
    testscenario_name = me.StringField(required=True)
    testcases = me.ListField(EmbeddedDocumentField(TestCases), required=True)