from flask import Flask
from flasgger import Swagger
from flask_restful import Api
from flask_restful import Resource, Api
from main.model.db import initialize_db
from main.controller.execute_controller import ExecuteAll
from main.controller.apis_controller import APIController
from main.controller.testcase_controller import TestCaseController
from main.utils.constants import *
from main.controller.services_controller import ServicesController
from main.controller.testScenario_controller import TestScenarioController

app = Flask(__name__)
api = Api(app)


# setting the config
app.config.from_object("config.Config")
if app.config["ENV"] == "stage":  # from terminal do : export FLASK_ENV=stage"
    app.config.from_object("config.StageConfig")
elif app.config["ENV"] == "uat":
    app.config.from_object("config.UATConfig")
else:
    app.config.from_object("config.ProdConfig")

print(f"Environment: {app.config['ENV']}")
print(f"Debug: {app.config['DEBUG']}")
print(f"DB_Name: {app.config['DB_NAME']}")

initialize_db(app.config['DB_NAME'], app.config['DB_URI'], app.config['DB_PORT'])

api.add_resource(ExecuteAll, EXECUTEALL_ENDPOINT)
api.add_resource(ServicesController, SERVICES_ENDPOINT)
api.add_resource(APIController, APIS_ENDPOINT)
api.add_resource(TestScenarioController, TESTSCENARIO_ENDPOINT)
api.add_resource(TestCaseController, TESTCASE_ENDPOINT)

if __name__ == '__main__':
    app.run(debug=True)