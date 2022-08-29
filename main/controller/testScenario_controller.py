from flask import Flask
from mongoengine import *
from flask_restful import Resource, Api, request, ResponseBase
from marshmallow import ValidationError

from main.service.testScenario_service import TestScenarioService
from main.utils.constants import *

class TestScenarioController(Resource):

    def get(self):

        query_parameters = request.args
        getTestScenario_obj = TestScenarioService()

        # if nothing provided in query parameters, return all services as key and list of their test scenarios as values of a dictionary
        if SERVICE not in query_parameters:
            return getTestScenario_obj.getTestScenarios()
        else:
            service_name = query_parameters[SERVICE]

        if TESTSCENARIO in query_parameters:  # return details of this particular testscenario
            return getTestScenario_obj.getTestScenarioDetails(service_name, query_parameters[TESTSCENARIO])
        else:  # return list of test scenarios of the service name provided
            return getTestScenario_obj.getTestScenarioList(service_name)

    def post(self):

        addTestScenario_obj = TestScenarioService()
        return addTestScenario_obj.addTestScenario()

    def delete(self):

        deleteTestScenario_obj = TestScenarioService()
        return deleteTestScenario_obj.deleteTestScenario()

    def patch(self):

        updateTestScenario_obj = TestScenarioService()
        return updateTestScenario_obj.updateTestScenario()