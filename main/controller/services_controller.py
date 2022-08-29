from flask import Flask
from flask_restful import Resource, Api, request, ResponseBase

from main.service.services_service import ListServices


class ServicesController(Resource):
    def get(self):
        servicename_obj = ListServices()
        return servicename_obj.getServiceNames(), 200