from main.model.apis_model import Apis
import logging
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import json
from main.utils.constants import *
import mongoengine
from main.model.testcases_model import TestCase
import requests

class APIService:
    def  getAPIDetails(self):
        args = request.args
        if args is not None:
            serviceName = args.get(SERVICE)

        if serviceName is None:
            api = Apis.objects()
        else:
            api = Apis.objects(service_name__iexact=serviceName)
            if len(api)==0:
                return {"message":"Api for this Service name not found. Please provide a valid service name"}, 404
        return json.loads(api.to_json()), 200

    def addAPI(self):
        request_payload = request.get_json()
        if not request_payload:
            return {"message": "Request payload not provided"}, 400

        # validate both keys and values of request payload
        try:
            Apis(**request_payload).validate()
        except (mongoengine.errors.ValidationError, mongoengine.errors.FieldDoesNotExist) as err:
            return {"message": "{0}".format(err)}, 422

        # check if such api already exists in database
        apis_obj = Apis.objects(service_name__iexact=request_payload[SERVICE_NAME_KEY],
                                api_name__iexact=request_payload[API_NAME_KEY])
        if len(apis_obj) != 0:
            return {"message": "API name provided already exists for this service."
                               " Please provide a different API name"}, 409

        # add api
        Apis(**request_payload).save()
        return {"message": "API blueprint added successfully"}, 201

    def deleteAPI(self):
        query_parameters = request.args

        # validate query parameters
        if SERVICE in query_parameters:
            service_name = query_parameters[SERVICE]
        else:
            return {"message": "Service name or query parameter is invalid"}, 400
        if API in query_parameters:
            api_name = query_parameters[API]
        else:
            return {"message": "API name or query parameter is invalid"}, 400

        # check whether requested api exists or not
        api_obj = Apis.objects(service_name__iexact=service_name, api_name__iexact=api_name)
        if len(api_obj) == 0:
            return {"message": "Requested API blueprint not found."
                               " Please provide an existing valid service name and api name"}, 404

        # check if any test case is associated with this api or not
        testcase_obj = TestCase.objects(service_name__iexact=service_name, api_name__iexact=api_name)
        if len(testcase_obj) != 0:
            testcase_json = testcase_obj.to_json()
            associated_testcases = [testcase[TC_NAME_KEY] for testcase in json.loads(testcase_json)]
            return {"message": "Can't delete API. Some test cases are associated with this api blueprint."
                               " To delete an API, make sure all associated test cases are deleted.",
                    "associated test cases": associated_testcases}, 400

        # delete api
        api_obj.delete()
        return {"message": "API blueprint deleted successfully"}, 200

    def updateAPI(self):
        query_parameters = request.args
        request_payload = request.get_json()

        # validate query parameters
        if SERVICE in query_parameters:
            old_service_name = query_parameters[SERVICE]
        else:
            return {"message": "Service name or query parameter is invalid"}, 400
        if API in query_parameters:
            old_api_name = query_parameters[API]
        else:
            return {"message": "API name or query parameter is invalid"}, 400

        # validate request payload
        if not request_payload:
            return {"message": "Request payload not provided"}, 400
        if SERVICE_NAME_KEY in request_payload:
            return {"message": "Service name can't be updated"}, 400

        # check whether requested api exists or not
        api_obj = Apis.objects(service_name__iexact=old_service_name, api_name__iexact=old_api_name)
        if len(api_obj) == 0:
            return {"message": "Requested API blueprint not found."
                               " Please provide an existing valid service name and api name"}, 404

        # if api name provided in request payload, check if it already exists in api collection
        if API_NAME_KEY in request_payload:
            api_obj1 = Apis.objects(service_name__iexact=old_service_name, api_name__iexact=request_payload[API_NAME_KEY])
            if len(api_obj1) != 0:
                return {"message": "API name provided in request payload for this service already exists in"
                                   " api collection. Please provide a different api name"}, 409

        # validate request payload (both keys and values) and update api
        try:
            api_obj.update(**request_payload)
        except (mongoengine.errors.ValidationError, mongoengine.errors.FieldDoesNotExist,
                mongoengine.errors.InvalidQueryError) as err:
            return {"message": "{0}".format(err)}, 422

        # if api name in request payload, update api name in associated test cases also
        if API_NAME_KEY in request_payload:
            testcase_obj = TestCase.objects(service_name__iexact=old_service_name, api_name__iexact=old_api_name)
            if len(testcase_obj) != 0:
                testcase_json = testcase_obj.to_json()
                associated_testcases = [testcase[TC_NAME_KEY] for testcase in json.loads(testcase_json)]
                req_payload = {API_NAME_KEY: request_payload[API_NAME_KEY]}
                for testcase in associated_testcases:
                    q_parameters = {SERVICE: old_service_name, TESTCASE: testcase}
                    response = requests.patch(BASE_URL + TESTCASE_ENDPOINT, json=req_payload, params=q_parameters)

                return {"message": "API blueprint and its associated test cases updated successfully",
                        "associated test cases": associated_testcases}, 200

        return {"message": "API blueprint updated successfully. No associated test cases found"}, 200