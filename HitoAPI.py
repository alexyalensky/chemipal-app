import time

import requests
from urllib import request


class HitoAPI:

    def __init__(self, domain, key):
        self.domain = domain
        self.key = key
        self.HEADERS = {
            "authorization": key,
            "Content-Type": "application/json"
        }

    def get_key(self):
        return self.key

    def get_users(self):
        url = self.domain + '/hito-rest/api/user'
        body = {}
        response_users = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_users.raise_for_status()
        request.urlcleanup()
        response_users.close()
        return response_users.json()['users']

    def get_user_params(self):
        url = self.domain + '/hito-rest/api/user'
        body = {}
        response_users = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_users.raise_for_status()
        request.urlcleanup()
        response_users.close()
        return response_users.json()['params']

    def get_entity_records(self, entity_num):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_num,
            "records": []
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        return response_entity.json()

    def get_specific_entity_records(self, entity_num, ids, params=[]):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_num,
            "params": params,
            "records": ids
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        request.urlcleanup()
        response_entity.close()
        return response_entity.json()

    def get_entity_records_based_on_params(self, entity_num, params):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_num,
            "params": params,
            "records": []
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        request.urlcleanup()
        response_entity.close()
        return response_entity.json()

    def get_entity_records_between_dates(self, entity_num, date_from, date_to):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_num,
            "records": [],
            "fromCreateDate": date_from,
            "toCreateDate": date_to
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        request.urlcleanup()
        response_entity.close()
        return response_entity.json()

    def get_entity_params(self, entity_num):
        url = self.domain + "/hito-rest/api/entity/params"
        body = {
            "entityId": entity_num
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        request.urlcleanup()
        response_entity.close()
        return response_entity.json()

    def get_last_param_id(self, entity_num):
        last_param = self.get_entity_params(entity_num)
        last_param.reverse()
        return last_param[0]['id']

    def get_specific_param_id(self, entity_num, location):
        specific_param = self.get_entity_params(entity_num)
        return (specific_param[location]['id'], specific_param[location]['type'])

    def create_or_update_one_record(self, entity_num, record_id, param):
        url = self.domain + "/hito-rest/api/entity/records/create-or-update"
        if 'valueId' in param and "value" in param:
            body = {
                "entityId": entity_num,
                "records": [
                    {
                        "recordId": record_id,
                        "paramValues": [
                            {
                                "id": param["id"],
                                "value": param["value"],
                                "valueId": param["valueId"]
                            }
                        ]
                    }
                ]
            }
        elif 'valueId' in param:
            body = {
                "entityId": entity_num,
                "records": [
                    {
                        "recordId": record_id,
                        "paramValues": [
                            {
                                "id": param["id"],
                                "valueId": param["valueId"]
                            }
                        ]
                    }
                ]
            }
        else:
            body = {
                "entityId": entity_num,
                "records": [
                    {
                        "recordId": record_id,
                        "paramValues": [
                            {
                                "id": param["id"],
                                "value": param["value"]
                            }
                        ]
                    }
                ]
            }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()

    def create_or_update_multi_records(self, body):
        url = self.domain + "/hito-rest/api/entity/records/create-or-update"
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()

    def get_headers(self, entity_num):
        params = self.get_entity_params(entity_num)
        headers = [param["name"] for param in params]
        return headers

    def get_param_value_ids(self, entity):
        param_value_ids = []
        for location in range(0, len(self.get_entity_params(entity))):
            param_value_ids.append(self.get_specific_param_id(entity, location))
        return param_value_ids

    def get_record_by_search_criteria(self, entity_id, param_id, operator, value):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_id,
            "searchCriterias": [
                {
                    "paramId": param_id,
                    "operator": operator,
                    "values": value
                }
            ]
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        return response_entity.json()

    def get_records_by_search_criteria_and_params(self, entity_id: int, params: list, searchCriterias=[]):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_id,
            "params": params,
            "searchCriterias": searchCriterias
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        return response_entity.json()

    def get_record_by_search_criterias(self, entity_id, searchCriterias):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_id,
            "searchCriterias": searchCriterias
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
        return response_entity.json()

    def add_update_users(self, users: list):
        url = self.domain + "/hito-rest/api/user/create-or-update"
        body = {
            "users": users
        }
        response = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response.raise_for_status()
