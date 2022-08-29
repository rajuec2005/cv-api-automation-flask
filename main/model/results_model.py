import mongoengine as me
from mongoengine import *
import mongoengine_goodjson as gj

class TestCases(EmbeddedDocument):
    tcName = StringField(required=True)
    URL = StringField(required=True)
    httpMethod = StringField(required=True)
    requestPayload = DictField()
    httpStatusCode = StringField()
    httpResponseMessage = StringField()
    headers = DictField()
    validation = ListField()
    status = StringField(required=True)
    jsonResponse = DictField()

class TestScenarios(EmbeddedDocument):
    serviceName = StringField(required=True)
    tsName = StringField(required=True)
    tsStatus = StringField(required=True)
    testCases = ListField(EmbeddedDocumentField(TestCases))

class TestExecutionDetails(EmbeddedDocument):
    testScenarios = ListField(EmbeddedDocumentField(TestScenarios))

class TestExecutionInput(EmbeddedDocument):
    serviceName = ListField(required=True)
    groups = ListField()
    testScenarioName = ListField()
    testEnv = StringField(required=True)
    testerEmailId = EmailField(required=True)

class Results(Document):
    uuid = StringField(required=True)
    testExecutionInput = ListField(EmbeddedDocumentField(TestExecutionInput))
    testExecutionDetails = ListField(EmbeddedDocumentField(TestExecutionDetails))