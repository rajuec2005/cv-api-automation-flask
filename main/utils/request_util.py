import requests
from config import *


class RequestUtil:
    # def __init__(self):
    #     self.headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': requests.post(Token_URL, json=Token_PAYLOAD).json()['authToken']
    #     }
    #     print("The token is ", self.headers)

    def getToken(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': requests.post(Token_URL, json=Token_PAYLOAD, verify=False).json()['authToken']
        }
        return headers

    def get(self, url, headers=None):
        if headers is None:
            headers = self.getToken()
        response = requests.get(url, headers=headers, verify=False)
        return response

    def post(self, url, payload, headers=None):
        if headers is None:
            headers = self.getToken()
        print("The header ", headers)
        print("The payload ", payload)
        response = requests.post(url, headers=headers, json=payload, verify=False)
        return response

    def put(self, url, payload, headers=None):
        if headers is None:
            headers = self.getToken()
        print("The header ", headers)
        print("The payload ", payload)
        response = requests.put(url, headers=headers, json=payload, verify=False)
        return response

    def patch(self, url, payload, headers=None):
        if headers is None:
            headers = self.getToken()
        print("The header ", headers)
        print("The payload ", payload)
        response = requests.patch(url, headers=headers, json=payload, verify=False)
        return response

    def delete(self, url, headers=None):
        if headers is None:
            headers = self.getToken()
        response = requests.delete(url, headers=headers, verify=False)
        return response