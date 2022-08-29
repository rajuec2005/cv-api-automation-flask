from main.model.testScenario_model import TestScenario
from main.model.testcases_model import TestCase
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from main.model.apis_model import Apis
from main.utils.constants import *
import mongoengine
import requests
import logging
import json


class TestCaseService:
    def getListOfTestCases(self):
        args = request.args
        # If service name is provided then listing all the tescases of that particular service
        if SERVICE in args:
            serviceName = args.get(SERVICE)
            testcase_obj = TestCase.objects(service_name__iexact=serviceName)
            # If service name provided does not exist
            if len(testcase_obj) == 0:
                return {"message": "Testcase for this Service name not found. Please provide a valid service name"}, 404
            else:
                testcase_list = [testcase[TC_NAME_KEY] for
                                 testcase in json.loads(testcase_obj.to_json())]
                return {"Service Name: {0}".format(serviceName): [
                    "Total Number of Testcase[s] found: {0}".format(len(testcase_list)), "Test Case List : {0}".format(
                        testcase_list)]}, 200
        # If no arguments are provided then list all the testcases based on their service name
        else:
            # Calling getServices api to get list of services
            services = requests.get(BASE_URL + SERVICES_ENDPOINT).json()
            list_of_testcases = {}
            # Listing tescases based on their service name
            for service_name in services:
                testcase_obj = TestCase.objects(service_name__iexact=service_name)
                if len(testcase_obj) != 0:
                    testcase_list = [testcase[TC_NAME_KEY] for
                                     testcase in json.loads(testcase_obj.to_json())]

                list_of_testcases[service_name] = ["Total No of testcase :{0}".format(len(testcase_list)),
                                                   testcase_list]

            return list_of_testcases, 200

    def getDetailsOfTestCase(self):
        args = request.args
        # Checking if query parameter is provided or not
        if SERVICE in request.args:
            serviceName = args.get(SERVICE)
        else:
            return {"message": "query parameter 'service' is NOT specified"}, 400
        testcaseName = args.get(TESTCASE)
        # getting details of the testcase
        testcase_obj = TestCase.objects(service_name__iexact=serviceName, tc_name__iexact=testcaseName)
        if len(testcase_obj) == 0:
            return {"message": "No matching testcase(s) found"}, 404
        return json.loads(testcase_obj.to_json()), 200

    def addTestCase(self):
        request_body = request.get_json()
        # Checking if request Pyload is empty
        if not request_body:
            return {"message": "Payload is required"}, 400

        # Checking If given payload is not valid as per Test Case Model
        try:
            TestCase(**request_body).validate()

        except (mongoengine.errors.ValidationError, mongoengine.errors.FieldDoesNotExist) as err:
            return {"message": "{0}".format(err)}, 422

        testcase = TestCase.objects(service_name=request_body[SERVICE_NAME_KEY], tc_name=request_body[TC_NAME_KEY])
        api = Apis.objects(service_name__iexact=request_body[SERVICE_NAME_KEY],
                           api_name__iexact=request_body[API_NAME_KEY])

        # Checking if Api for the testcase we want to add, exists or not
        if len(api) == 0:
            return {"message": "Api blueprint'{0}' for this test case does not exist. Please add api first".format(
                request_body[API_NAME_KEY])}, 400
        # Checking if Testcase we want to add, already exists or not
        elif len(testcase) == 0:
            TestCase(**request_body).save()
            return {"message": "Test case added successfully"}, 201
        else:
            return {
                       "message": "Test Case '{0}' for this service already exists. Please provide a different Test Case name".format(
                           request_body[TC_NAME_KEY])}, 409

    def deleteTestCase(self):
        args = request.args
        # Handling if No arguments are provided
        if not args:
            return {"message": "Query parameters 'service' and 'testcase' not provided"}, 400
        # Checking if either of the query parameters is not provided
        if SERVICE in request.args:
            serviceName = args.get(SERVICE)
        else:
            return {"message": "Query parameter 'service' is NOT specified"}, 400
        if TESTCASE in request.args:
            testcaseName = args.get(TESTCASE)
        else:
            return {"message": "Query parameter 'testcase' is NOT specified"}, 400
        # Searching the testcase we want to delete in database
        testcase = TestCase.objects(service_name__iexact=serviceName, tc_name__iexact=testcaseName)

        # If no such testcase exist in database
        if len(testcase) == 0:
            return {"message": "No matching testcase(s) found"}, 404
        # Checking if any TestScenarios are associated with this testcase we want delete
        testscenarios_obj = TestScenario.objects(service_name__iexact=serviceName,
                                                 testcases__tc_name__iexact=testcaseName)
        if len(testscenarios_obj) != 0:
            testscenario_json = json.loads(testscenarios_obj.to_json())
            testscenario_list = [testscenario[TESTSCENARIO_NAME_KEY] for testscenario in testscenario_json]
            return {
                       "message": "This test case is being used in test scenarios {0}. Please delete or update Test Scenario first".format(
                           testscenario_list)}, 400
        # Delete the testcase
        testcase.delete()
        return {"message": "Testcase Deleted Successfully"}, 200

    def updateTestCase(self):
        args = request.args
        # Handling if no arguments are provided
        if not args:
            return {"message": "Query parameters 'service' and 'testcase' not provided"}, 400
        # Checking if either of the arguments are absent
        if SERVICE in request.args:
            serviceName = args.get(SERVICE)
        else:
            return {"message": "Query parameter 'service' is NOT specified"}, 400
        if TESTCASE in request.args:
            testcaseName = args.get(TESTCASE)
        else:
            return {"message": "Query parameter 'testcase' is NOT specified"}, 400

        # Handling if request payload is empty
        request_body = request.get_json()
        if not request_body:
            return {"message": "Provide payload to update the test case"}, 400

        # Checking if service name is there in the request payload
        if SERVICE_NAME_KEY in request_body:
            return {"message": "Service name can't be updated"}, 400

        # Searching the testcase given to update in database
        testcase = TestCase.objects(service_name__iexact=serviceName, tc_name__iexact=testcaseName)

        # If No such testcase exists
        if len(testcase) == 0:
            return {
                       "message": "Test Case '{0}' for service '{1}' does not exists. Please provide a different Test Case name".format(
                           testcaseName, serviceName)}, 404
        # If new testcase name given in payload already exists
        if TC_NAME_KEY in request_body:
            new_testcase = TestCase.objects(service_name__iexact=serviceName, tc_name__iexact=request_body[TC_NAME_KEY])
            if len(new_testcase) != 0:
                return {
                    "message": "Test case name provided in request payload for this service already exists. Please provide a different test case name"},409

        # If given api name in payload is not present in APIS table
        if API_NAME_KEY in request_body:
            api = Apis.objects(service_name__iexact=serviceName, api_name__iexact=request_body[API_NAME_KEY])
            if len(api) == 0:
                return {"message": "Api blueprint '{0}' does not exist. Please add or update api first".format(
                    request_body[API_NAME_KEY])}, 400

        # Checking If given payload is not valid as per Test Case Model
        try:
            testcase.update(**request_body)

        except (mongoengine.errors.InvalidQueryError, mongoengine.errors.ValidationError) as err:
            return {"message": "{0}".format(err)}, 422

        # If testcase name is getting updated then updating the testcase in testscenario as well
        if TC_NAME_KEY in request_body:
            testscenarios = TestScenario.objects(service_name__iexact=serviceName,
                                                 testcases__tc_name__iexact=testcaseName)
            if len(testscenarios) != 0:
                list_testscenario = json.loads(testscenarios.to_json())
                associated_ts = []
                for testscenario in list_testscenario:
                    testcase_list = []
                    associated_ts.append(testscenario[TESTSCENARIO_NAME_KEY])
                    for testcase_dict in testscenario[TESTCASES_KEY]:
                        if testcase_dict[TC_NAME_KEY].casefold() == testcaseName.casefold():
                            testcase_dict[TC_NAME_KEY] = request_body[TC_NAME_KEY]
                        testcase_list.append(testcase_dict)

                    query_parameters = {
                        SERVICE: serviceName,
                        TESTSCENARIO: testscenario[TESTSCENARIO]
                    }
                    update_testscenario_url = BASE_URL + TESTSCENARIO_ENDPOINT
                    json_payload = {TESTCASES_KEY: testcase_list}

                    response = requests.patch(update_testscenario_url, json=json_payload, params=query_parameters)

        return {"message": "Testcase and its associated testscenarios {0} updated Successfully".format(
            associated_ts)}, 200

        return {"message": "Testcase updated Successfully"}, 200