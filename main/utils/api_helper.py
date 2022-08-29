from requests import Response

from main.utils.request_util import RequestUtil
from MOCK_SERVER_config import *
from main.model.testcases_model import TestCase
from main.model.apis_model import Apis


class APIHelper:

    def __init__(self, testcaseobj: TestCase, apiobj: Apis, responseDict):
        self.testCaseName = testcaseobj.tc_name
        self.payload = testcaseobj.request_payload
        self.hostName = SR_HOSTNAME
        self.uri = apiobj.uri
        self.uri_params = testcaseobj.uri_params
        self.http_method = apiobj.http_method
        self.port = PORT
        self.resultDict = responseDict
        self.retry = testcaseobj.retry
        self.retrycount = testcaseobj.retrycount
        self.validation = testcaseobj.validation
        self.executionStatus = False
        self.validationDict = {}  # to store validation results (expected and actual)

    def checkIfResponseJsonIsNotEmpty(self, testcasename):
        try:
            print(self.resultDict[testcasename].json())
            return True
        except ValueError:
            return False

    def formRequest(self):
        print("Inside formrequest")
        if bool(self.uri_params):
            print("The uri params is present")
            if bool(self.resultDict):
                print("The result dict is present")
                for i in range(len(self.uri_params)):
                    if bool(self.uri_params[i].api_reference):
                        print("The api reference is true")
                        value = self.resultDict[self.uri_params[i].tc_name].json()[self.uri_params[i].value]
                        print("The value is "+value)
                        self.uri = self.uri.replace(self.uri_params[i].name, value)

        self.uri = "https://" + self.hostName + ":" + self.port + self.uri
        print("The formed Base URI ", self.uri)


    def validator(self):
        print("inside validator for TC ", self.testCaseName)
        self.checkIfResponseJsonIsNotEmpty(self.testCaseName)
        status = True
        if bool(self.validation):
            for i in range(len(self.validation)):
                if bool(self.validation[i].http_status_code):
                    print("Verify statuscode is present")
                    print("The expected status code ", self.validation[i].http_status_code)
                    print("The actual status code ", self.resultDict[self.testCaseName].status_code)
                    self.validationDict["expected_http_status_code"] = self.validation[i].http_status_code
                    self.validationDict["actual_http_status_code"] = str(self.resultDict[self.testCaseName].status_code)
                    if self.validation[i].http_status_code == str(
                            self.resultDict[self.testCaseName].status_code):
                        status = True
                    else:
                        status = False
                        return status
                    print("Status code validation is ", status)

                if bool(self.validation[i].http_response_message):
                    print("Verify response message is present")
                    print("The expected response message ", self.validation[i].http_response_message)
                    print("The actual response message  ", self.resultDict[self.testCaseName].reason)
                    self.validationDict["expected_http_response_message"] = self.validation[i].http_response_message
                    self.validationDict["actual_http_response_message"] = self.resultDict[self.testCaseName].reason
                    if self.validation[i].http_response_message.lower() == self.resultDict[self.testCaseName].reason.lower():
                        status = True
                    else:
                        status = False
                        return status
                    print("Status message validation is ", status)

                if bool(self.validation[i].http_response_body):
                    print("Verify httpresponsebody is present")
                    if bool(self.checkIfResponseJsonIsNotEmpty(self.testCaseName)):
                        json = self.resultDict[self.testCaseName].json()
                        http_response_body = self.validation[i].http_response_body
                        print("The http_response_body ", http_response_body)
                        self.validationDict["http_response_body"] = []
                        for i in range(len(http_response_body)):
                            # create a dictionary to capture the expected and actual responses
                            # and then append it to validationDict["http_response_body"]
                            new_dict = {}
                            new_dict["expected value for json path: {}".format(http_response_body[i].json_path)] =  http_response_body[i].value
                            new_dict["actual value for json path: {}".format(http_response_body[i].json_path)] = json[http_response_body[i].json_path]
                            self.validationDict["http_response_body"].append(new_dict)
                            if http_response_body[i].value == json[http_response_body[i].json_path]:
                                status = True
                            else:
                                status = False
                                break
        return status