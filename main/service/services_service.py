from main.model.apis_model import Apis
from main.utils.constants import *
import json


class ListServices:
    def getServiceNames(self):
        apis = Apis.objects().to_json()
        services_list = []
        for api_data in json.loads(apis):
            service_name = (api_data[SERVICE_NAME_KEY]).lower()
            if service_name not in services_list:
                services_list.append(service_name)
        services_list.sort()
        return services_list