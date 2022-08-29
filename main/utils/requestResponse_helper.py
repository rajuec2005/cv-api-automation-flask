from main.model.results_model import *
import json
from main.utils.constants import SENSITIVE_HEADERS

class RequestResponseHelper:

    def __init__(self):
        self.testCasesList = []
        self.testScenariosList = []

    # this method will create a testCaseObj, set the fields and append it to testCasesList initialized in __init__
    # the apiHelperObj contains all the information required
    def setTestCase(self, apiHelperObj, result):
        testCasesObj = TestCases()
        testCasesObj.tcName = apiHelperObj.testCaseName
        testCasesObj.URL = apiHelperObj.uri
        testCasesObj.httpMethod = apiHelperObj.http_method
        testCasesObj.requestPayload = apiHelperObj.payload

        # if resultDict contains response of this testcase name, set the required fields
        if apiHelperObj.testCaseName in apiHelperObj.resultDict:
            testCasesObj.httpStatusCode = str(apiHelperObj.resultDict[apiHelperObj.testCaseName].status_code)
            testCasesObj.httpResponseMessage = apiHelperObj.resultDict[apiHelperObj.testCaseName].reason

            # mask the sensitive fields of headers
            headers = dict(apiHelperObj.resultDict[apiHelperObj.testCaseName].headers)
            common_keys = headers.keys() & SENSITIVE_HEADERS
            for key in common_keys:
                headers[key] = "sensitive information hidden"
            testCasesObj.headers = headers

            # check if json response is not empty and add it to the collection
            if bool(apiHelperObj.checkIfResponseJsonIsNotEmpty(apiHelperObj.testCaseName)):
                testCasesObj.jsonResponse = dict(apiHelperObj.resultDict[apiHelperObj.testCaseName].json())

        testCasesObj.status = result[apiHelperObj.testCaseName]["status"]
        testCasesObj.validation = [apiHelperObj.validationDict]

        # for each test case, add the test case object to this testCaseList
        self.testCasesList.append(testCasesObj)

    # this method will create the testScenarioObj, set the fields including testcases and append it to the
    # testScenarioList initialised in __init
    def setTestScenario(self, testscenario, isTSPassed: bool):

        testScenariosObj = TestScenarios()
        testScenariosObj.serviceName = testscenario.service_name
        testScenariosObj.tsName = testscenario.testscenario_name
        tcList = self.testCasesList[:]
        testScenariosObj.testCases = tcList
        testScenariosObj.tsStatus = "PASSED" if isTSPassed else "FAILED"

        self.testScenariosList.append(testScenariosObj)
        self.testCasesList.clear()

    # this method will create a resultsObj, set the execution_input and execution_details fields and push it to the database
    def setResult(self, executeRequestObj, uid):
        resultsObj = Results(uuid=uid)
        testExecutionDetailsObj = TestExecutionDetails(testScenarios=self.testScenariosList)
        testExecutionInputObj = TestExecutionInput(serviceName=executeRequestObj.serviceName, groups=executeRequestObj.groups,
                                                   testScenarioName=executeRequestObj.testscenario_name,
                                                   testEnv=executeRequestObj.testEnv,
                                                   testerEmailId=executeRequestObj.testerEmailId)
        resultsObj.testExecutionInput = [testExecutionInputObj]
        resultsObj.testExecutionDetails = [testExecutionDetailsObj]
        resultsObj.save()