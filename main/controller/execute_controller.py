from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, request, ResponseBase
from marshmallow import ValidationError
from main.service.execute_service import ExecuteService

from main.schema.execute_request_schema import ExecuteRequestSchema


class ExecuteAll(Resource):
    def post(self):
        json_data = request.get_json()

        if not json_data:
            return {"message": "No input data provided"}, 400

        try:
            executeRequestSchema = ExecuteRequestSchema()
            executeRequestObj = executeRequestSchema.load(json_data)
            print(executeRequestObj)

        except ValidationError as err:
            return err.messages, 422

        executeServiceObj = ExecuteService()
        return executeServiceObj.executeTests(executeRequestObj), 200

    def get(self):
        executeServiceObj = ExecuteService()
        return executeServiceObj.executeTests(), 200