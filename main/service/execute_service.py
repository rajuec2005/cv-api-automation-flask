from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from flask import jsonify

import logging
from main.model.apis_model import Apis
from main.model.testcases_model import TestCase
from main.schema.execute_request_schema import ExecuteRequestSchema, RequestSchema
from main.model.testScenario_model import TestScenario
from main.utils.api_helper import APIHelper
from main.utils.request_util import RequestUtil
import requests
from config import *
import uuid
import datetime
from main.utils.requestResponse_helper import RequestResponseHelper
from main.utils.reporter_util.report_helper import ReportHelper
from main.utils.email_util.email_helper import EmailHelper
request = RequestUtil()

class ExecuteService:

    def execute(self):
        pass

    def executeTests(self, executeRequestObj: RequestSchema):
        uid = self.createLogFileAndGenerateUid()
        logging.info("UUID " + uid)
        overall = {}
        testScenarios = self.getTestScenariosList(executeRequestObj)

        # initialize a requestResponseHelper, set the fields and push it to database
        requestResponseHelperObj = RequestResponseHelper()
        for testscenario in testScenarios:
            validationPassed = True
            result = {}
            responseDict = {}
            # declare a boolean to check the status(passed/failed) of test scenario
            isTSPassed = True
            logging.info("Executing Test Scenario: " + testscenario.testscenario_name)
            for i in range(len(testscenario.testcases)):
                testCaseObj = self.getTestCaseObj(testscenario.testcases[i].tc_name,
                                                  testscenario.service_name)
                apiObj = self.getAPIObj(testCaseObj, testscenario.service_name)
                if bool(validationPassed):
                    apiHelperObj = self.executeTestCase(testCaseObj,
                                                        apiObj,
                                                        result, responseDict)
                    if not bool(apiHelperObj.executionStatus):
                        validationPassed = False
                        # if any test case failed/skipped, set the tsStatus to failed
                        isTSPassed = False
                        # break
                else:
                    apiHelperObj = self.getApiHelperObj(testCaseObj, apiObj, responseDict)

                    result[testscenario.testcases[i].tc_name] = {"status": "SKIPPED",
                                                                 "jsonResponse": {}}
                logging.info("After Execution")
                logging.info(apiHelperObj.testCaseName)
                logging.info(apiHelperObj.executionStatus)
                logging.info(apiHelperObj.uri)

                # call the setTestCase method to create a testCaseObj, set the fields and append it to a test case list
                requestResponseHelperObj.setTestCase(apiHelperObj, result)

            # call the setTestScenario method to create a testScenarioObj and append testCaseObj to it
            requestResponseHelperObj.setTestScenario(testscenario, isTSPassed)

            overall["uuid"] = uid
            overall[testscenario.testscenario_name] = result

        # call setResult to set the execution_input and execution_details fields and push it to database
        requestResponseHelperObj.setResult(executeRequestObj, uid)

        # ReportHelper will generate the html report and save it to output folder
        report_obj = ReportHelper(uid)
        report_obj.generateReport()

        # caputre the tester's email id and send an email containing a html table of test summary and html report as an attachment
        RECEIVER_ADDR.append(executeRequestObj.testerEmailId)
        email_obj = EmailHelper(uid)
        email_obj.sendMail()

        logging.info(overall)
        logging.info("API Test Execution Completed")
        logging.getLogger().handlers.clear()
        return overall

    def getTestScenariosList(self, executeRequestObj: RequestSchema):
        logging.info("API Tests Execution")
        if executeRequestObj.groups is not None and executeRequestObj.testscenario_name is not None:
            if "ALL" in executeRequestObj.serviceName:
                return TestScenario.objects(groups__in=executeRequestObj.groups,
                                            testscenario_name__in=executeRequestObj.testscenario_name)
            else:
                return TestScenario.objects(service_name__in=executeRequestObj.serviceName,
                                            groups__in=executeRequestObj.groups,
                                            testscenario_name__in=executeRequestObj.testscenario_name)
        elif executeRequestObj.groups is not None and executeRequestObj.testscenario_name is None:
            if "ALL" in executeRequestObj.serviceName:
                return TestScenario.objects(groups__in=executeRequestObj.groups)
            else:
                return TestScenario.objects(service_name__in=executeRequestObj.serviceName,
                                            groups__in=executeRequestObj.groups)
        elif executeRequestObj.groups is None and executeRequestObj.testscenario_name is not None:
            if "ALL" in executeRequestObj.serviceName:
                return TestScenario.objects(testscenario_name__in=executeRequestObj.testscenario_name)
            else:
                return TestScenario.objects(service_name__in=executeRequestObj.serviceName,
                                            testscenario_name__in=executeRequestObj.testscenario_name)
        elif executeRequestObj.groups is None and executeRequestObj.testscenario_name is None:
            if executeRequestObj.serviceName == "ALL":
                return TestScenario.objects()
            else:
                return TestScenario.objects(service_name__in=executeRequestObj.serviceName)

    def getTestCaseObj(self, testcasename, servicename):
        testCaseObj = TestCase.objects(tc_name=testcasename, service_name=servicename, disable=False).first()
        return testCaseObj

    def getAPIObj(self, testcaseobj: TestCase, servicename):
        apiObj = Apis.objects(service_name=servicename, api_name=testcaseobj.api_name).first()
        return apiObj

    def getApiHelperObj(selfself, testCaseObj: TestCase, apiObj, responseDict):
        apihelperObj = APIHelper(testCaseObj, apiObj, responseDict)
        return apihelperObj

    def executeTestCase(self, testCaseObj, apiObj, result, responseDict):
        return self.executeAPIs(testCaseObj, apiObj, result, responseDict)
        # if bool(self.executeAPIs(testCaseObj, apiObj, result, responseDict)):
        #     logging.debug("Continue execution")
        #     return True
        # else:
        #     logging.debug("Skip remaining testcases in this test scenario, proceed to next test scenario")
        #     return False

    def executeAPIs(self, testCaseObj, apiObj, result, responseDict):
        executionstatus = True
        apiHelper = self.getApiHelperObj(testCaseObj, apiObj, responseDict)
        apiHelper.formRequest()
        logging.info(" Executing testcase :" + apiHelper.testCaseName)
        logging.info(" The base URI :" + apiHelper.uri)
        logging.info(" HTTP Method :" + apiHelper.http_method)
        if apiHelper.retry:
            for i in range(apiHelper.retrycount):
                responseDict[apiHelper.testCaseName] = self.executeAPI(apiHelper)
                if bool(apiHelper.validator()):
                    executionstatus = True
                    break
                else:
                    executionstatus = False
        else:
            responseDict[apiHelper.testCaseName] = self.executeAPI(apiHelper)
            if bool(apiHelper.validator()):
                executionstatus = True
            else:
                executionstatus = False
        self.setResultJson(executionstatus, apiHelper.checkIfResponseJsonIsNotEmpty(apiHelper.testCaseName),apiHelper.testCaseName,
                           result,responseDict)
        logging.debug("API Validation status " + str(executionstatus))
        print("The execution status is :", executionstatus)
        apiHelper.executionStatus = executionstatus
        return apiHelper

    def setResultJson(self, executionstatus, isResponseJsonEmpty, testCaseName, result, responseDict):

        if executionstatus:
            if isResponseJsonEmpty:
                result[testCaseName] = {"status": "PASSED",
                                        "jsonResponse": responseDict[testCaseName].json()}
            else:
                result[testCaseName] = {"status": "PASSED", "jsonResponse": {}}
        else:
            if isResponseJsonEmpty:
                result[testCaseName] = {"status": "FAILED",
                                        "jsonResponse": responseDict[testCaseName].json()}
            else:
                result[testCaseName] = {"status": "FAILED", "jsonResponse": {}}

    def executeAPI(self, apihelper):
        if apihelper.http_method.upper() == 'GET':
            response = request.get(apihelper.uri)
            # responseDict[apihelper.testCaseName] = response

        elif apihelper.http_method.upper() == "POST":
            logging.debug("Executing post")
            response = request.post(apihelper.uri, apihelper.payload)
            # responseDict[apihelper.testCaseName] = response

        elif apihelper.http_method.upper() == "PUT":
            logging.debug("Executing PUT")
            response = request.put(apihelper.uri)
            logging.debug("The status code ", response.status_code)
            # responseDict[apihelper.testCaseName] = response

        elif apihelper.http_method.upper() == "PATCH":
            logging.debug("Executing PATCH")
            response = request.patch(apihelper.uri)
            logging.debug("The status code ", response.status_code)
            # responseDict[apihelper.testCaseName] = response

        elif apihelper.http_method.upper() == "DELETE":
            logging.debug("Executing Delete")
            response = request.delete(apihelper.uri)
            logging.debug("The status code ", response.status_code)
            # responseDict[apihelper.testCaseName] = response

        logging.debug("The status code :" + str(response.status_code))
        # return apihelper.validator()
        return response

    def createLogFileAndGenerateUid(self):
        print("Create log")
        uid = str(uuid.uuid4())
        logging.basicConfig(level=logging.DEBUG)
        log_file_format = "[%(levelname)s] - %(asctime)s : %(message)s"
        handler = RotatingFileHandler(uid + '.log', mode='w', backupCount=0)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(log_file_format))
        logging.getLogger().addHandler(handler)
        return uid