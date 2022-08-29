from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, request, ResponseBase
from marshmallow import ValidationError
from main.service.apis_service import APIService

class  APIController(Resource):

    def get(self):
        getAPIDetails_obj=APIService()
        return  getAPIDetails_obj.getAPIDetails()

    def post(self):
        addAPI_obj = APIService()
        return addAPI_obj.addAPI()

    def delete(self):
        deleteAPI_obj = APIService()
        return deleteAPI_obj.deleteAPI()

    def patch(self):
        updateAPI_obj = APIService()
        return updateAPI_obj.updateAPI()