import time

import requests
from urllib import request
from logging_config import get_logger

logger = get_logger(__name__)


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

    def _make_request(self, method, url, **kwargs):
        """
        Internal method to make HTTP requests with logging and error handling.
        
        Args:
            method: HTTP method (currently only 'POST' is used)
            url: Full URL to request
            **kwargs: Additional arguments passed to requests.post
            
        Returns:
            Response object
        """
        # Extract useful logging information
        body = kwargs.get('json', {})
        entity_id = body.get('entityId') if isinstance(body, dict) else 'N/A'
        record_count = len(body.get('records', [])) if isinstance(body, dict) and 'records' in body else 0
        
        # Log request
        logger.debug(f'API Request: {method} {url} | Entity: {entity_id} | Records: {record_count}')
        
        try:
            # Add timeout to all requests
            kwargs['timeout'] = kwargs.get('timeout', 30)
            
            # Make request
            response = requests.post(url, **kwargs)
            
            # Log successful response
            duration = response.elapsed.total_seconds()
            logger.debug(f'API Response: {response.status_code} | Duration: {duration:.2f}s | Entity: {entity_id}')
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.Timeout as e:
            logger.error(f'API Timeout: {method} {url} | Entity: {entity_id} | Duration: 30s+')
            raise
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'
            logger.error(f'API Error: {method} {url} | Status: {status_code} | Entity: {entity_id}')
            raise

    def get_users(self):
        url = self.domain + '/hito-rest/api/user'
        body = {}
        response_users = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        request.urlcleanup()
        response_users.close()
        return response_users.json()['users']

    def get_user_params(self):
        url = self.domain + '/hito-rest/api/user'
        body = {}
        response_users = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        request.urlcleanup()
        response_users.close()
        return response_users.json()['params']

    def get_entity_records(self, entity_num):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_num,
            "records": []
        }
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        return response_entity.json()

    def get_specific_entity_records(self, entity_num, ids, params=[]):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_num,
            "params": params,
            "records": ids
        }
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
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
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
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
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        request.urlcleanup()
        response_entity.close()
        return response_entity.json()

    def get_entity_params(self, entity_num):
        url = self.domain + "/hito-rest/api/entity/params"
        body = {
            "entityId": entity_num
        }
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
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
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)

    def create_or_update_multi_records(self, body):
        url = self.domain + "/hito-rest/api/entity/records/create-or-update"
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)

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
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        return response_entity.json()

    def get_records_by_search_criteria_and_params(self, entity_id: int, params: list, searchCriterias=[]):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_id,
            "params": params,
            "searchCriterias": searchCriterias
        }
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        return response_entity.json()

    def get_record_by_search_criterias(self, entity_id, searchCriterias):
        url = self.domain + "/hito-rest/api/entity/records"
        body = {
            "entityId": entity_id,
            "searchCriterias": searchCriterias
        }
        response_entity = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
        return response_entity.json()

    def add_update_users(self, users: list):
        url = self.domain + "/hito-rest/api/user/create-or-update"
        body = {
            "users": users
        }
        response = self._make_request('POST', url, headers=self.HEADERS, json=body, verify=False)
