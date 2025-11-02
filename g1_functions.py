from datetime import datetime
from HitoAPI import HitoAPI
import logging
from logging_config import setup_logging, get_logger

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)


def check_for_new_users(customer_api: HitoAPI, entity_id: int, search_criteria: list[dict], params: list[int]) -> tuple[bool, list, list]:
    """
        Checks whether new users exist in the specified entity based on provided search criteria and parameters.
        Args:
            customer_api (HitoAPI): An instance of the HitoAPI class, representing the customer's API connection.
                This object is used to perform the search and must be properly authenticated and initialized.

            entity_id (int): The ID of the entity in which to search for new users.

            search_criteria (list): A list containing a dictionaries that defines the search filter.
                The dictionaries must follow the exact structure:
                    {
                        "paramId": int,
                        "operator": str,
                        "values": list[str]
                    }

                - `paramId`: The ID of the parameter (field) to filter by.
                - `operator`: The comparison operator to use.

            params (list): A list of integers representing additional parameter IDs to include in the search.

        Returns:
            tuple:
                - bool: True if any matching records (new users) were found, otherwise False.
                - list: A list of user records (dictionaries) that matched the search criteria, or an empty list if none were found.
        """
    new_users = customer_api.get_records_by_search_criteria_and_params(
        entity_id=entity_id,
        searchCriterias=search_criteria,
        params=params
    )
    if new_users.get("records"):
        return True, new_users["records"], new_users["params"]
    else:
        return False, [], []

def transform_user_record(user: dict) -> dict:
    """
    Transforms a user record from the G1 API into a standardized format.
    :param user: A dictionary representing a user record from the G1 API.
    :return: A dictionary with transformed user data.
    """
    return {
        "id": user["paramValues"][0].get("value"),
        "paramValues": [
            {"id": 2, "value": user["paramValues"][0].get("value")},  # username
            {"id": 1030, "valueId": user["paramValues"][1].get("valueId"), "value": user["paramValues"][1].get("value")},  # G1Relation
            {"id": 4, "value": user["paramValues"][2].get("value")},  # First Name
            {"id": 3, "value": user["paramValues"][3].get("value")},  # Last Name
            {"id": 5, "value": 1},  # Active
            {"id": 18, "value": user["paramValues"][4].get("value", "")},  # main phone
            {"id": 17, "value": user["paramValues"][5].get("value", "")},  # email
            {"id": 1048, "valueId": user["paramValues"][10].get("valueId", 999), "value": user["paramValues"][10].get("value", "ללא")},  # licenseCompanyCode
            {"id": 1049, "valueId": user["paramValues"][11].get("valueId", 999), "value": user["paramValues"][11].get("value", "ללא")},  # licenseCompanyBranch
            {"id": 1068, "valueId": user["paramValues"][12].get("valueId", 999), "value": user["paramValues"][12].get("value", "אין סטטוס")},  # doingTestDrive
            {"id": 1070, "value": user["paramValues"][6].get("value", "")},  # drivingLicenseNum
            {"id": 1071, "value": datetime.strptime(user["paramValues"][7].get("value", ""), "%Y-%m-%d").strftime("%d/%m/%Y") if user["paramValues"][7].get("value", "") else ""},  # drivingLicenseDate
            {"id": 1072, "value": datetime.strptime(user["paramValues"][9].get("value", ""), "%Y-%m-%d").strftime("%d/%m/%Y") if user["paramValues"][9].get("value", "") else ""},
            {"id": 1073, "value": user["paramValues"][8].get("value", "")},  # drivingLicenseType
        ]
    }


def are_mandatory_values_valid(params: list[dict], mandatory_set: set[int]) -> bool:
    """
    Check if all mandatory items have a valid 'value' field (exists and not empty/whitespace).

    :param params: List of dictionaries
    :param mandatory_set: List of valueId's that are considered mandatory
    :return: True if all mandatory items have a valid 'value', False otherwise
    """
    for param in params:
        if param.get("valueId") in mandatory_set:
            value = param.get("value")
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return False
    return True


def create_users_from_entity_rows(customer_api: HitoAPI, entity_id: int, search_criteria: list[dict], entity_params: list[int]) -> bool:
    """
    Creates new users in the specified entity based on search criteria and parameters.
    Args:
        customer_api (HitoAPI): An instance of the HitoAPI class, representing the customer's API connection.
            This object is used to perform the search and must be properly authenticated and initialized.
        entity_id (int): The ID of the entity in which to search for new users.
        search_criteria (list): A list containing dictionaries that define the search filter.
            The dictionaries must follow the exact structure:
                {
                    "paramId": int,
                    "operator": str,
                    "values": list[str]
                }
                - `paramId`: The ID of the parameter (field) to filter by.
                - `operator`: The comparison operator to use.
        entity_params (list): A list of integers representing additional parameter IDs to include in the search
    Returns:
        bool: True if new users were successfully created, False otherwise.
    """
    logging.info(f'Checking for new users in {customer_api.domain} in entity {entity_id}...')
    new_users_found, new_users, params = check_for_new_users(customer_api, entity_id, search_criteria, entity_params)
    if not new_users_found:
        logging.info(f'No new users found in entity {entity_id} for {customer_api.domain}.')
        return False
    else:
        new_users_body = []
        mandatory_ids = {574, 627, 628, 570}
        users_body_to_update_status = {
            "entityId": entity_id,
            "records": []
        }
        logging.info(f'Found {len(new_users)} new users in entity {entity_id}. Validating mandatory fields...')
        for user in new_users:
            if are_mandatory_values_valid(user["paramValues"], mandatory_ids):
                new_users_body.append(transform_user_record(user))
                users_body_to_update_status["records"].append({"recordId": user["recordId"], "paramValues": [{"id": 989, "valueId": 3, "value": "הוקם כמשתמש"}]})
        if not new_users_body:
            logging.info(f'No valid users found to create in entity {entity_id} for {customer_api.domain}.')
            return False
        try:
            logging.info(f'Creating {len(new_users_body)} new users from entity {entity_id} for {customer_api.domain}...')
            customer_api.add_update_users(new_users_body)
        except Exception as e:
            logging.error(f'Error creating new users for {customer_api.domain}: {e}')
            return False
        else:
            try:
                logging.info(f'Updating user status for {len(users_body_to_update_status["records"])} users in entity {entity_id} for {customer_api.domain}...')
                customer_api.create_or_update_multi_records(users_body_to_update_status)
            except Exception as e:
                logging.error(f'Error updating user status for {customer_api.domain}: {e}')
                return False
            logging.info(f'Successfully created new users and updated their status in entity {entity_id} for {customer_api.domain}.')
            return True
