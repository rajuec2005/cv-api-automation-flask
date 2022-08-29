from main.utils.constants import *
from main.model.testScenario_model import TestScenario
from main.model.testcases_model import TestCase
import mongoengine
from flask_restful import Resource, Api, request, ResponseBase
import json
import requests

class TestScenarioService:

    # this method will be called when no query parameters are passed.
    # It will return all service names and their test scenarios as list
    def getTestScenarios(self):

        # get list of service names using "services_service" api
        services_list = requests.get(BASE_URL + SERVICES_ENDPOINT)
        # create a dictionary to store service name as key and list of all test scenarios of this service as value
        my_dict = {}

        total_test_scenarios = 0
        for service_name in services_list.json():
            testscenario_obj = TestScenario.objects(service_name__iexact=service_name)
            if len(testscenario_obj) != 0:
                testscenario_list = [testscenario[TESTSCENARIO_NAME_KEY] for
                                     testscenario in json.loads(testscenario_obj.to_json())]
                my_dict[service_name] = testscenario_list
                total_test_scenarios += len(testscenario_list)

        my_dict["total test scenarios"] = total_test_scenarios
        return my_dict, 200

    # this method will be called when only service name provided in query parameters.
    # it will return all test scenarios of this service and their number
    def getTestScenarioList(self, service_name):

        testscenario_obj = TestScenario.objects(service_name__iexact=service_name)

        if len(testscenario_obj) == 0:
            return {"message": "No test scenario found for this service"}, 404
        else:
            testscenario_list = [testscenario[TESTSCENARIO_NAME_KEY] for
                                 testscenario in json.loads(testscenario_obj.to_json())]
            return {"message": "{0} test scenarios found for {1}".format(len(testscenario_list), service_name),
                    "test scenarios": testscenario_list}, 200

    # this method will be called when both service name and test scenario name provided in query parameters
    # it will return all the details of this particular test scenario
    def getTestScenarioDetails(self, service_name, testscenario_name):

        testscenario_obj = TestScenario.objects(service_name__iexact=service_name,
                                                testscenario_name__iexact=testscenario_name)

        if len(testscenario_obj) == 0:
            return {"message": "Requested test scenario not found."
                               " Please provide an existing valid service name and test scenario name"}, 404
        else:
            return json.loads(testscenario_obj.to_json()), 200

    def addTestScenario(self):

        request_payload = request.get_json()
        if not request_payload:
            return {"message": "Request payload not provided"}, 400

        # validate both key and values of request payload
        try:
            TestScenario(**request_payload).validate()
        except (mongoengine.errors.ValidationError, mongoengine.errors.FieldDoesNotExist) as err:
            return {"message": "{0}".format(err)}, 422

        # check if such test scenario already exists in database
        testscenario_obj = TestScenario.objects(testscenario_name__iexact=request_payload[TESTSCENARIO_NAME_KEY],
                                                service_name__iexact=request_payload[SERVICE_NAME_KEY])
        if len(testscenario_obj) != 0:
            return {"message": "Test scenario for this service already exists."
                               " Please provide a different test scenario name"}, 409

        # check whether test cases provided in request payload are in test case collection or not
        testcases = [testcase[TC_NAME_KEY] for testcase in request_payload[TESTCASES_KEY]]
        missing_testcases = []
        for testcase in testcases:
            testcase_obj = TestCase.objects(service_name__iexact=request_payload[SERVICE_NAME_KEY],
                                            tc_name__iexact=testcase)
            if len(testcase_obj) == 0:
                missing_testcases.append(testcase)
        if len(missing_testcases) != 0:
            return {"message": "following test cases of this test scenario not found in test case collection."
                               " Please add these test cases first",
                    "missing testcases": missing_testcases}, 400

        # add test scenario
        TestScenario(**request_payload).save()
        return {"message": "Test scenario added successfully"}, 201

    def deleteTestScenario(self):
        query_parameters = request.args

        # validate query parameters
        if SERVICE in query_parameters:
            service_name = query_parameters[SERVICE]
        else:
            return {"message": "Service name or query parameter is invalid"}, 400
        if TESTSCENARIO in query_parameters:
            testscenario_name = query_parameters[TESTSCENARIO]
        else:
            return {"message": "Test scenario name or query parameter is invalid"}, 400

        # check whether requested test scenario exists or not
        testscenario_obj = TestScenario.objects(service_name__iexact=service_name,
                                                testscenario_name__iexact=testscenario_name)
        if len(testscenario_obj) == 0:
            return {"message": "Requested test scenario not found."
                               " Please provide an existing valid service name and test scenario name"}, 404

        # delete test scenario
        testscenario_obj.delete()
        return {"message": "Test scenario deleted successfully"}, 200

    def updateTestScenario(self):
        query_parameters = request.args
        request_payload = request.get_json()

        # validate query parameters
        if SERVICE in query_parameters:
            service_name = query_parameters[SERVICE]
        else:
            return {"message": "Service name or query parameter is invalid"}, 400
        if TESTSCENARIO in query_parameters:
            testscenario_name = query_parameters[TESTSCENARIO]
        else:
            return {"message": "Test scenario name or query parameter is invalid"}, 400

        # validate request payload
        if not request_payload:
            return {"message": "Request payload not provided"}, 400
        if SERVICE_NAME_KEY in request_payload:
            return {"message": "Service name can't be updated"}, 400

        # check whether requested test scenario exists or not
        testscenario_obj = TestScenario.objects(service_name__iexact=service_name,
                                                testscenario_name__iexact=testscenario_name)
        if len(testscenario_obj) == 0:
            return {"message": "Requested test scenario not found."
                               " Please provide an existing valid service name and test scenario name"}, 404

        # if test scenario provided in request payload, check if it already exists for this service
        if TESTSCENARIO_NAME_KEY in request_payload:
            testscenario_obj1 = TestScenario.objects(service_name__iexact=service_name,
                                                    testscenario_name__iexact=request_payload[TESTSCENARIO_NAME_KEY])
            if len(testscenario_obj1) != 0:
                return {"message": "Test scenario name provided in request payload for this service already exists"
                                   " in test scenario collection. Please provide a different test scenario name"}, 409

        # if test cases provided in request payload, check whether those test cases exist in test case collection or not
        testcases = [testcase[TC_NAME_KEY] for testcase in request_payload[TESTCASES_KEY]]
        missing_testcases = []
        for testcase in testcases:
            testcase_obj = TestCase.objects(service_name__iexact=service_name,
                                            tc_name__iexact=testcase)
            if len(testcase_obj) == 0:
                missing_testcases.append(testcase)
        if len(missing_testcases) != 0:
            return {"message": "following test cases of this test scenario not found in test case collection."
                               " Please add these test cases in test case collection first",
                    "missing testcases": missing_testcases}, 400

        # validate request payload(both keys and values) and update test scenario
        try:
            testscenario_obj.update(**request_payload)
        except (mongoengine.errors.FieldDoesNotExist, mongoengine.errors.InvalidQueryError) as err:
            return {"message": "{0}".format(err)}, 422

        return {"message": "Test scenario updated successfully"}, 200