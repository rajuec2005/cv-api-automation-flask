from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, request, ResponseBase
from marshmallow import ValidationError
from main.service.testcase_service import TestCaseService
from main.model.testcases_model import TestCase
from main.utils.constants import *


class TestCaseController(Resource):
    def get(self):
        testcaseservice_obj = TestCaseService()
        args = request.args
        if args is not None and TESTCASE in args:
            return testcaseservice_obj.getDetailsOfTestCase()
        else:
            return testcaseservice_obj.getListOfTestCases()

    def post(self):
        testcaseservice_obj = TestCaseService()
        return testcaseservice_obj.addTestCase()

    def delete(self):
        testcaseservice_obj = TestCaseService()
        return testcaseservice_obj.deleteTestCase()

    def patch(self):
        testcaseservice_obj = TestCaseService()
        return testcaseservice_obj.updateTestCase()