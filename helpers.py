import logging
from datetime import datetime
from logging_config import get_logger

logger = get_logger(__name__)


def remove_hyphens(phone_number):
    return phone_number.replace("-", "")


def format_the_date(date):
    return date.replace("-", "/")


def get_last_id(api, entity_num, param_id):
    last_id = 1
    entity = api.get_entity_records_based_on_params(entity_num=entity_num, params=[param_id])
    if "records" not in entity:
        return last_id
    else:
        for record in entity["records"]:
            if int(record["recordId"]) > last_id:
                last_id = int(record["recordId"])
    last_id += 1
    return last_id


# This function transfer rows from one entity to another
# it transfers only rows based on search criteria
def entity2entity(api, origin_entity_id, dest_entity_id, search_criteria, param_ids_to_transfer, param_ids_to_receive,
                  program_status_param_id):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity - START -----------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity - '
        f'FROM ENTITY {origin_entity_id} TO ENTITY {dest_entity_id} -----------------!')
    try:
        results = api.get_records_by_search_criteria_and_params(
            entity_id=origin_entity_id,
            params=param_ids_to_transfer,
            searchCriterias=search_criteria
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity'
            f' - END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {origin_entity_id}  -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity - '
            f'ERROR MESSAGE {e} -----------------!')
        return False
    if "records" not in results:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity - END '
            f'NO RECORDS WERE FOUND IN ORIGIN ENTITY  -----------------!')
        return False
    else:
        dest_entity_body = {
            "entityId": dest_entity_id,
            "records": []
        }
        origin_entity_body = {
            "entityId": origin_entity_id,
            "records": []
        }
        for record in results["records"]:
            dest_record = {
                "recordId": "auto",
                "paramValues": []
            }
            for loc in range(len(param_ids_to_transfer)):
                if "value" in (record["paramValues"][loc]) and "valueId" in (record["paramValues"][loc]):
                    dest_record["paramValues"].append({
                        "id": param_ids_to_receive[loc],
                        "value": record["paramValues"][loc]["value"],
                        "valueId": record["paramValues"][loc]["valueId"]
                    })
                    continue
                if "value" in (record["paramValues"][loc]):
                    dest_record["paramValues"].append({
                        "id": param_ids_to_receive[loc],
                        "value": record["paramValues"][loc]["value"]
                    })
            dest_entity_body["records"].append(dest_record)
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [
                    {
                        "id": program_status_param_id,
                        "valueId": 6
                    }
                ]
            })
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity -'
                f' TRY TO UPDATE RECORDS {origin_entity_body} -----------------!')
            api.create_or_update_multi_records(origin_entity_body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity -'
                f' END WITH ERRORS TRYING TO UPDATE {origin_entity_body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity -'
                f' ERROR MESSAGE {e} -----------------!')
            return False
        else:
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity -'
                    f' TRY TO CREATE RECORDS {dest_entity_body} -----------------!')
                api.create_or_update_multi_records(dest_entity_body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity -'
                    f' END WITH ERRORS TRYING TO CREATE {dest_entity_body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity -'
                    f' ERROR MESSAGE {e} -----------------!')
                return False
            else:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity2entity - END '
                    f'-----------------!')
                return True


# This function return True if it finds the param value based search criteria in entity
def is_param_exists_in_entity(search_criteria, entity_id, api):
    results = api.get_record_by_search_criterias(entity_id=entity_id, searchCriterias=search_criteria)
    if "records" in results:
        return True
    return False


# This function transfer value from origin entity to destination entity
# based on params values equality just like Hito's entities rules
def entity_param_2_entity_param(api, origin_entity_id: int, dest_entity_id: int, origin_param_id_to_find: int,
                                dest_param_id_to_find: int, origin_param_id_to_transfer: int,
                                dest_param_id_to_recieve: int):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - START ---'
        f'--------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
        f'FROM ENTITY {origin_entity_id} TO ENTITY {dest_entity_id} '
        f'TRANSFER VALUE FROM PARAM ID {origin_param_id_to_transfer} TO PARAM ID'
        f' {dest_param_id_to_recieve} -----------------!')
    try:
        dest_entity_found_records = api.get_records_by_search_criteria_and_params(
            entity_id=dest_entity_id,
            params=[dest_param_id_to_find, dest_param_id_to_recieve],
            searchCriterias=[
                {
                    "paramId": dest_param_id_to_recieve,
                    "operator": "E"
                }
            ]
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - END WITH ERRORS'
            f'COULD NOT GET RECORDS FROM ENTITY {dest_entity_id}  -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
            f'ERROR MESSAGE {e} -----------------!')
        return
    if "records" not in dest_entity_found_records:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - END '
            f' NO RECORDS FOUND TO GET PARAMS  -----------------!')
        return
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - FOUND RECORDS IN'
        f'DESTINATION ENTITY - {dest_entity_id} THE RECORDS ARE - {dest_entity_found_records} -----------------!')
    value_to_look_in_origin = ""
    dest_entity_body = {
        "entityId": dest_entity_id,
        "records": []
    }
    for dest_record in dest_entity_found_records["records"]:
        if dest_record["paramValues"][0].get("value") is None:
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param'
                         f' dest_record["paramValues"][0].get("value") None -  is {dest_record} -----------------!')
            continue
        if value_to_look_in_origin != dest_record["paramValues"][0].get("value"):
            try:
                origin_entity_found_records = api.get_records_by_search_criteria_and_params(
                    entity_id=origin_entity_id,
                    params=[origin_param_id_to_transfer],
                    searchCriterias=[
                        {
                            "paramId": origin_param_id_to_find,
                            "operator": "EQ",
                            "values": [dest_record["paramValues"][0].get("value")]
                        }
                    ]
                )
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
                    f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {origin_entity_id}  -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
                    f'ERROR MESSAGE {e} -----------------!')
                return
            if "records" not in origin_entity_found_records:
                continue
            if origin_entity_found_records["records"][0]["paramValues"][0].get("value") is None:
                continue
            if "valueId" in origin_entity_found_records["records"][0]["paramValues"][0]:
                dest_entity_body["records"].append({
                    "recordId": dest_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": dest_param_id_to_recieve,
                            "value": origin_entity_found_records["records"][0]["paramValues"][0].get("value"),
                            "valueId": origin_entity_found_records["records"][0]["paramValues"][0].get("valueId")
                        }
                    ]
                })
                continue
            dest_entity_body["records"].append({
                "recordId": dest_record.get("recordId"),
                "paramValues": [
                    {
                        "id": dest_param_id_to_recieve,
                        "value": origin_entity_found_records["records"][0]["paramValues"][0].get("value")
                    }
                ]
            })
    if len(dest_entity_body["records"]) < 1:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' END SUCCESSFULLY WITH NO RECORDS TO UPDATE -----------------!')
        return
    try:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' TRY TO UPDATE RECORDS {dest_entity_body} -----------------!')
        api.create_or_update_multi_records(dest_entity_body)
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' END WITH ERRORS TRYING TO UPDATE {dest_entity_body} -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' ERROR MESSAGE {e} -----------------!')
        return
    else:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' END SUCCESSFULLY -----------------!')


# This function transfer value from origin entity to destination entity
# based on search criteria equality just like Hito's entities rules
def entity_param_2_entity_param_by_criteria(api, origin_entity_id: int, dest_entity_id: int,
                                            origin_param_id_to_find: int,
                                            dest_param_id_to_find: int, origin_param_id_to_transfer: int,
                                            dest_param_id_to_recieve: int, search_criteria: list):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - START ---'
        f'--------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
        f'FROM ENTITY {origin_entity_id} TO ENTITY {dest_entity_id} '
        f'TRANSFER VALUE FROM PARAM ID {origin_param_id_to_transfer} TO PARAM ID'
        f' {dest_param_id_to_recieve} -----------------!')
    try:
        dest_entity_found_records = api.get_records_by_search_criteria_and_params(
            entity_id=dest_entity_id,
            params=[dest_param_id_to_find, dest_param_id_to_recieve],
            searchCriterias=search_criteria
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - END WITH ERRORS'
            f'COULD NOT GET RECORDS FROM ENTITY {dest_entity_id}  -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
            f'ERROR MESSAGE {e} -----------------!')
        return
    if "records" not in dest_entity_found_records:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - END '
            f' NO RECORDS FOUND TO GET PARAMS  -----------------!')
        return
    value_to_look_in_origin = ""
    dest_entity_body = {
        "entityId": dest_entity_id,
        "records": []
    }
    for dest_record in dest_entity_found_records["records"]:
        if dest_record["paramValues"][0].get("value") is None:
            continue
        if value_to_look_in_origin != dest_record["paramValues"][0].get("value"):
            try:
                values = dest_record["paramValues"][0].get("value")
                origin_entity_found_records = api.get_records_by_search_criteria_and_params(
                    entity_id=origin_entity_id,
                    params=[origin_param_id_to_transfer],
                    searchCriterias=[
                        {
                            "paramId": origin_param_id_to_find,
                            "operator": "EQ",
                            "values": [values]
                        }
                    ]
                )
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
                    f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {origin_entity_id}  -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param - '
                    f'ERROR MESSAGE {e} -----------------!')
                return
            if "records" not in origin_entity_found_records:
                continue
            if origin_entity_found_records["records"][0]["paramValues"][0].get("value") is None:
                continue
            if "valueId" in origin_entity_found_records["records"][0]["paramValues"][0]:
                dest_entity_body["records"].append({
                    "recordId": dest_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": dest_param_id_to_recieve,
                            "value": origin_entity_found_records["records"][0]["paramValues"][0].get("value"),
                            "valueId": origin_entity_found_records["records"][0]["paramValues"][0].get("valueId")
                        }
                    ]
                })
                continue
            dest_entity_body["records"].append({
                "recordId": dest_record.get("recordId"),
                "paramValues": [
                    {
                        "id": dest_param_id_to_recieve,
                        "value": origin_entity_found_records["records"][0]["paramValues"][0].get("value")
                    }
                ]
            })
    if len(dest_entity_body["records"]) < 1:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' END SUCCESSFULLY WITH NO RECORDS TO UPDATE -----------------!')
        return
    try:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' TRY TO UPDATE RECORDS {dest_entity_body} -----------------!')
        api.create_or_update_multi_records(dest_entity_body)
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' END WITH ERRORS TRYING TO UPDATE {dest_entity_body} -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' ERROR MESSAGE {e} -----------------!')
        return
    else:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_param_2_entity_param -'
            f' END SUCCESSFULLY -----------------!')


def entity_2_users_delek(api, entity_id, criteria_param_id, criteria_value, criteria_value_id_after_move_to_user,
                         entity_params_to_transfer):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek - START ---'
        f'--------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek - ENTITY {entity_id} '
        f'TO USERS -----------------!')
    try:
        found_records = api.get_records_by_search_criteria_and_params(
            entity_id=entity_id,
            params=entity_params_to_transfer,
            searchCriterias=[
                {
                    "paramId": criteria_param_id,
                    "operator": "EQ",
                    "values": [criteria_value]
                }
            ]
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek - '
            f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {entity_id}  -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek - '
            f'ERROR MESSAGE {e} -----------------!')
        return
    else:
        if "records" in found_records:
            users = []
            entity_body = {
                "entityId": entity_id,
                "records": []
            }
            for record in found_records["records"]:
                entity_body["records"].append(
                    {
                        "recordId": record["recordId"],
                        "paramValues": [
                            {
                                "id": criteria_param_id,
                                "valueId": criteria_value_id_after_move_to_user
                            }
                        ]
                    }
                )
                first_name = record["paramValues"][1].get("value")
                last_name = record["paramValues"][2].get("value")
                sug_hafaala_id = record["paramValues"][5].get("valueId")
                sug_hafaala_name = record["paramValues"][5].get("value")
                if record["paramValues"][0].get("value") == 1 or record["paramValues"][0].get("value") == '1':
                    new_id = 1001
                    username = 1001
                else:
                    new_id = record["paramValues"][0].get("value")
                    username = record["paramValues"][0].get("value")
                if "valueId" not in record["paramValues"][5]:
                    active = 0
                    users.append(
                        {
                            "id": new_id,
                            "paramValues": [
                                {
                                    "id": 4,
                                    "value": first_name
                                },
                                {
                                    "id": 3,
                                    "value": "תחנה יצאה מדלק"
                                },
                                {
                                    "id": 5,
                                    "value": active
                                },
                                {
                                    "id": 2,
                                    "value": username
                                },
                                {
                                    "id": 1009,
                                    "value": sug_hafaala_name,
                                    "valueId": sug_hafaala_id
                                }
                            ]
                        }
                    )
                    continue
                if record["paramValues"][5].get("valueId") == 4 or record["paramValues"][5].get("valueId") == '4':
                    active = 0
                    users.append(
                        {
                            "id": new_id,
                            "paramValues": [
                                {
                                    "id": 4,
                                    "value": first_name
                                },
                                {
                                    "id": 3,
                                    "value": "תחנה יצאה מדלק"
                                },
                                {
                                    "id": 5,
                                    "value": active
                                },
                                {
                                    "id": 2,
                                    "value": username
                                },
                                {
                                    "id": 1009,
                                    "value": sug_hafaala_name,
                                    "valueId": sug_hafaala_id
                                }
                            ]
                        }
                    )
                    continue
                else:
                    active = 1
                if record["paramValues"][7].get("value") == "1":
                    medicine = 1
                else:
                    medicine = 0
                email = record["paramValues"][3].get("value")
                direct_manager = record["paramValues"][4].get("valueId")
                phone = record["paramValues"][6].get("value")
                users.append(
                    {
                        "id": new_id,
                        "paramValues": [
                            {
                                "id": 4,
                                "value": first_name
                            },
                            {
                                "id": 3,
                                "value": last_name
                            },
                            {
                                "id": 5,
                                "value": active
                            },
                            {
                                "id": 2,
                                "value": username
                            },
                            {
                                "id": 1003,
                                "value": "תחנה",
                                "valueId": 3
                            },
                            {
                                "id": 7,
                                "value": direct_manager
                            },
                            {
                                "id": 11,
                                "value": "מנהל תחנה",
                                "valueId": 99
                            },
                            {
                                "id": 1009,
                                "value": sug_hafaala_name,
                                "valueId": sug_hafaala_id
                            },
                            {
                                "id": 17,
                                "value": email
                            },
                            {
                                "id": 18,
                                "value": phone
                            },
                            {
                                "id": 1011,
                                "value": medicine
                            }
                        ]
                    }
                )
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                    f' TRY TO UPDATE USER {users} -----------------!')
                api.add_update_users(users)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                    f' END WITH ERRORS TRYING TO UPDATE USERS {users} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                    f' ERROR MESSAGE {e} -----------------!')
                return
            else:
                try:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                        f' TRY TO UPDATE ENTITY {entity_id} WITH {entity_body} -----------------!')
                    api.create_or_update_multi_records(entity_body)
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                        f' END WITH ERRORS TRYING TO UPDATE ENTITY {entity_id} WITH {entity_body} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                        f' ERROR MESSAGE {e} -----------------!')
                    return
                else:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                        f' END SUCCESSFULLY -----------------!')
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users_delek -'
                f' NO NEW RECORDS FOUND END SUCCESSFULLY -----------------!')


# This function changes param value based on another param if the other param is not empty
def change_param_value_based_on_another_param_is_not_empty(api, entity_id: int, dest_param: dict,
                                                           search_criteria: list):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- '
        f'change_param_value_based_on_another_param_is_not_empty - START -----------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- change_param_value_'
        f'based_on_another_param_is_not_empty - ENTITY {entity_id} -----------------!')
    try:
        entity_found_records = api.get_records_by_search_criteria_and_params(
            entity_id=entity_id,
            params=[search_criteria[0]["paramId"]],
            searchCriterias=search_criteria
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- '
            f'change_param_value_based_on_another_param_is_not_empty - '
            f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {entity_id} -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- '
            f'change_param_value_based_on_another_param_is_not_empty - ERROR MESSAGE {e} -----------------!')
        return
    else:
        if "records" in entity_found_records:
            new_entity_body = {
                "entityId": entity_id,
                "records": []
            }
            for record in entity_found_records["records"]:
                new_entity_body["records"].append({
                    "recordId": record["recordId"],
                    "paramValues": [dest_param]
                })
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- '
                    f'change_param_value_based_on_another_param_is_not_empty -'
                    f' TRY TO UPDATE ENTITY {entity_id} WITH {new_entity_body} -----------------!')
                api.create_or_update_multi_records(new_entity_body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- '
                    f'change_param_value_based_on_another_param_is_not_empty -'
                    f' END WITH ERRORS TRYING TO UPDATE ENTITY {entity_id} WITH {new_entity_body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- '
                    f'change_param_value_based_on_another_param_is_not_empty - ERROR MESSAGE {e} -----------------!')
                return
            else:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- change_param_value_based_'
                    f'on_another_param_is_not_empty - END SUCCESSFULLY -----------------!')
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- change_param_value_based_'
                f'on_another_param_is_not_empty - NO NEW RECORDS FOUND END SUCCESSFULLY -----------------!')

def transfer_volunteers(
        customer_name,
        api,
        origin_entity_id,
        dest_entity_id,
        search_criteria,
        param_ids_to_transfer,
        param_ids_to_receive,
        program_status_param_id,
        update_origin_entity_with_tz_without_zero_param):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - START -----------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - '
        f'FROM ENTITY {origin_entity_id} TO ENTITY {dest_entity_id} -----------------!')
    try:
        results = api.get_records_by_search_criteria_and_params(
            entity_id=origin_entity_id,
            params=param_ids_to_transfer,
            searchCriterias=search_criteria
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name}'
            f' - END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {origin_entity_id}  -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - '
            f'ERROR MESSAGE {e} -----------------!')
        return False
    if "records" not in results:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - END '
            f'NO RECORDS WERE FOUND IN ORIGIN ENTITY  -----------------!')
        return False
    else:
        dest_entity_body = {
            "entityId": dest_entity_id,
            "records": []
        }
        origin_entity_body = {
            "entityId": origin_entity_id,
            "records": []
        }
        for record in results["records"]:
            last_record_error = False
            dest_record = {
                "recordId": "",
                "paramValues": []
            }
            for loc in range(len(param_ids_to_transfer)):
                if loc == 0:
                    if "value" in (record["paramValues"][loc]):
                        if record["paramValues"][loc]["value"].isnumeric():
                            if int(record["paramValues"][loc]["value"]) != 0:
                                try:
                                    is_vol_exists = api.get_records_by_search_criteria_and_params(
                                        entity_id=dest_entity_id,
                                        params=[param_ids_to_receive[0]],
                                        searchCriterias=[{
                                            "paramId": param_ids_to_receive[0],
                                            "operator": "EQ",
                                            "values": [int(record["paramValues"][loc]["value"])]
                                        }]
                                    )
                                except Exception as e:
                                    logging.info(
                                        f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name}'
                                        f' - END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {origin_entity_id}  -----------------!')
                                    logging.info(
                                        f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - '
                                        f'ERROR MESSAGE {e} -----------------!')
                                    break
                                else:
                                    if "records" in is_vol_exists:
                                        origin_entity_body["records"].append({
                                            "recordId": record["recordId"],
                                            "paramValues": [{
                                                "id": program_status_param_id,
                                                "valueId": 2,
                                                "value": "נבדק - תקין"
                                            }]
                                        })
                                        last_record_error = True
                                        break
                                    else:
                                        dest_record["recordId"] = int(record["paramValues"][loc]["value"])
                                        dest_record["paramValues"].append({
                                            "id": param_ids_to_receive[loc],
                                            "value": record["paramValues"][loc]["value"]
                                        })
                                        continue
                            else:
                                origin_entity_body["records"].append({
                                    "recordId": record["recordId"],
                                    "paramValues": [{
                                        "id": program_status_param_id,
                                        "valueId": 3,
                                        "value": "נבדק - תז לא תקין"
                                    }]
                                })
                                last_record_error = True
                                break
                        else:
                            origin_entity_body["records"].append({
                                "recordId": record["recordId"],
                                "paramValues": [{
                                    "id": program_status_param_id,
                                    "valueId": 3,
                                    "value": "נבדק - תז לא תקין"
                                }]
                            })
                            last_record_error = True
                            break
                    else:
                        origin_entity_body["records"].append({
                            "recordId": record["recordId"],
                            "paramValues": [{
                                "id": program_status_param_id,
                                "valueId": 3,
                                "value": "נבדק - תז לא תקין"
                            }]
                        })
                        last_record_error = True
                        break
                if "value" in (record["paramValues"][loc]) and "valueId" in (record["paramValues"][loc]):
                    dest_record["paramValues"].append({
                        "id": param_ids_to_receive[loc],
                        "value": record["paramValues"][loc]["value"],
                        "valueId": record["paramValues"][loc]["valueId"]
                    })
                    continue
                if "value" in (record["paramValues"][loc]):
                    dest_record["paramValues"].append({
                        "id": param_ids_to_receive[loc],
                        "value": record["paramValues"][loc]["value"]
                    })
            if last_record_error:
                continue
            dest_entity_body["records"].append(dest_record)
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [
                    {
                        "id": program_status_param_id,
                        "valueId": 2
                    },
                    {
                        "id": update_origin_entity_with_tz_without_zero_param,
                        "value": dest_record["recordId"]
                    }
                ]
            })
        if len(origin_entity_body["records"]) > 0:
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} -'
                    f' TRY TO UPDATE RECORDS {origin_entity_body} -----------------!')
                api.create_or_update_multi_records(origin_entity_body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} -'
                    f' END WITH ERRORS TRYING TO UPDATE {origin_entity_body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} -'
                    f' ERROR MESSAGE {e} -----------------!')
                return False
            else:
                if len(dest_entity_body["records"]) > 0:
                    try:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} -'
                            f' TRY TO CREATE RECORDS {dest_entity_body} -----------------!')
                        api.create_or_update_multi_records(dest_entity_body)
                    except Exception as e:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} -'
                            f' END WITH ERRORS TRYING TO CREATE {dest_entity_body} -----------------!')
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} -'
                            f' ERROR MESSAGE {e} -----------------!')
                        return False
                    else:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - END '
                            f'-----------------!')
                        return True
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- transfer_volunteers {customer_name} - END '
            f'-----------------!')
        return False


def entity_2_users(api, entity_id, criteria_param_id, criteria_value, criteria_value_id_after_move_to_user,
                   entity_params_to_transfer, users_params, username_id_from_entity, username_id_from_users,
                   id_id_from_entity, date_ids_list, user_active_id, send_sms=False):
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users - START ---'
        f'--------------!')
    logging.info(
        f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users - ENTITY {entity_id} '
        f'TO USERS -----------------!')
    try:
        found_records = api.get_records_by_search_criteria_and_params(
            entity_id=entity_id,
            params=entity_params_to_transfer,
            searchCriterias=[
                {
                    "paramId": criteria_param_id,
                    "operator": "EQ",
                    "values": [criteria_value]
                }
            ]
        )
    except Exception as e:
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users - '
            f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {entity_id}  -----------------!')
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users - '
            f'ERROR MESSAGE {e} -----------------!')
        return
    else:
        if "records" not in found_records:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users -'
                f' NO NEW RECORDS FOUND END SUCCESSFULLY -----------------!')
            return
        else:
            users = []
            entity_body = {
                "entityId": entity_id,
                "records": []
            }
            for record in found_records["records"]:
                if "value" not in record["paramValues"][0]:
                    entity_body["records"].append(
                        {
                            "recordId": record["recordId"],
                            "paramValues": [
                                {
                                    "id": criteria_param_id,
                                    "valueId": 4
                                }
                            ]
                        }
                    )
                    continue
                if not record["paramValues"][0]["value"].isdigit():
                    entity_body["records"].append(
                        {
                            "recordId": record["recordId"],
                            "paramValues": [
                                {
                                    "id": criteria_param_id,
                                    "valueId": 4
                                }
                            ]
                        }
                    )
                    continue
                if "value" not in record["paramValues"][1]:
                    entity_body["records"].append(
                        {
                            "recordId": record["recordId"],
                            "paramValues": [
                                {
                                    "id": criteria_param_id,
                                    "valueId": 5
                                }
                            ]
                        }
                    )
                    continue
                if not remove_hyphens(record["paramValues"][1]["value"]).isdigit():
                    entity_body["records"].append(
                        {
                            "recordId": record["recordId"],
                            "paramValues": [
                                {
                                    "id": criteria_param_id,
                                    "valueId": 5
                                }
                            ]
                        }
                    )
                    continue
                user = {
                    "id": int(record["paramValues"][0]["value"]),
                    "paramValues": []
                }
                entity_body["records"].append(
                    {
                        "recordId": record["recordId"],
                        "paramValues": [
                            {
                                "id": criteria_param_id,
                                "valueId": criteria_value_id_after_move_to_user
                            }
                        ]
                    }
                )
                user["paramValues"].append({
                    "id": user_active_id,
                    "value": 1
                })
                for loc in range(len(entity_params_to_transfer)):
                    if entity_params_to_transfer[loc] == id_id_from_entity:
                        continue
                    if entity_params_to_transfer[loc] in date_ids_list:
                        if "value" in record["paramValues"][loc]:
                            user["paramValues"].append({
                                "id": users_params[loc],
                                "value": format_the_date(record["paramValues"][loc]["value"])
                            })
                            continue
                        else:
                            continue
                    if entity_params_to_transfer[loc] == username_id_from_entity:
                        user["paramValues"].append({
                            "id": username_id_from_users,
                            "value": int(remove_hyphens(record["paramValues"][loc]["value"]))
                        })
                        user["paramValues"].append({
                            "id": users_params[loc],
                            "value": remove_hyphens(record["paramValues"][loc]["value"])
                        })
                        continue
                    if "value" in (record["paramValues"][loc]) and "valueId" in (record["paramValues"][loc]):
                        user["paramValues"].append({
                            "id": users_params[loc],
                            "value": record["paramValues"][loc]["value"],
                            "valueId": record["paramValues"][loc]["valueId"]
                        })
                        continue
                    if "value" in (record["paramValues"][loc]):
                        user["paramValues"].append({
                            "id": users_params[loc],
                            "value": record["paramValues"][loc]["value"]
                        })
                users.append(user)
            if len(users) < 1:
                return
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users -'
                    f' TRY TO UPDATE USER {users} -----------------!')
                api.add_update_users(users)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users -'
                    f' END WITH ERRORS TRYING TO UPDATE USERS {users} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users -'
                    f' ERROR MESSAGE {e} -----------------!')
                return
            else:
                if len(entity_body["records"]) < 1:
                    return
                try:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- '
                        f'entity_2_users - TRY TO UPDATE ENTITY {entity_id} WITH {entity_body} -----------------!')
                    api.create_or_update_multi_records(entity_body)
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- '
                        f'entity_2_users -'
                        f' END WITH ERRORS TRYING TO UPDATE ENTITY {entity_id} WITH {entity_body} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- '
                        f'entity_2_users - ERROR MESSAGE {e} -----------------!')
                    return
                else:
                    if send_sms:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users -'
                            f' END SUCCESSFULLY -----------------!')
                        return users
                    else:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- entity_2_users -'
                            f' END SUCCESSFULLY -----------------!')

def transfer_records_based_on_blocks(customer_name, api, origin_entity_id, dest_entity_id, search_criteria,
                                     param_ids_to_transfer, param_ids_to_receive, program_status_param_id,
                                     block_param_pos, new_id_pos):
    try:
        results = api.get_records_by_search_criteria_and_params(
            entity_id=origin_entity_id,
            params=param_ids_to_transfer,
            searchCriterias=search_criteria
        )
    except Exception as e:
        logger.error(f'transfer_records_based_on_blocks | Customer: {customer_name} | FAILED to get records from entity {origin_entity_id} | Error: {e}', exc_info=True)
        return None  # None = error occurred
    if "records" not in results or len(results.get("records", [])) == 0:
        return False
    else:
        dest_entity_body = {
            "entityId": dest_entity_id,
            "records": []
        }
        origin_entity_body = {
            "entityId": origin_entity_id,
            "records": []
        }
        for record in results["records"]:
            if "valueId" not in record["paramValues"][block_param_pos]:
                origin_entity_body["records"].append({
                    "recordId": record["recordId"],
                    "paramValues": [{
                        "id": program_status_param_id,
                        "valueId": 3,
                        "value": "נבדק - לא תקין"
                    }]
                })
                continue
            elif "value" not in record["paramValues"][new_id_pos]:
                origin_entity_body["records"].append({
                    "recordId": record["recordId"],
                    "paramValues": [{
                        "id": program_status_param_id,
                        "valueId": 3,
                        "value": "נבדק - לא תקין"
                    }]
                })
                continue
            elif not record["paramValues"][new_id_pos]["value"].isnumeric():
                origin_entity_body["records"].append({
                    "recordId": record["recordId"],
                    "paramValues": [{
                        "id": program_status_param_id,
                        "valueId": 3,
                        "value": "נבדק - לא תקין"
                    }]
                })
                continue
            elif (int(record["paramValues"][new_id_pos]["value"]) == 0 or
                  int(record["paramValues"][new_id_pos]["value"]) < 0):
                origin_entity_body["records"].append({
                    "recordId": record["recordId"],
                    "paramValues": [{
                        "id": program_status_param_id,
                        "valueId": 3,
                        "value": "נבדק - לא תקין"
                    }]
                })
                continue
            else:
                new_record_id = (str(record["paramValues"][new_id_pos]["value"]) +
                                 str(record["paramValues"][block_param_pos]["valueId"]))
                dest_record = {
                    "recordId": int(new_record_id),
                    "paramValues": []
                }
                for loc in range(len(param_ids_to_transfer)):
                    if "value" in (record["paramValues"][loc]) and "valueId" in (record["paramValues"][loc]):
                        dest_record["paramValues"].append({
                            "id": param_ids_to_receive[loc],
                            "value": record["paramValues"][loc]["value"],
                            "valueId": record["paramValues"][loc]["valueId"]
                        })
                        continue
                    if "value" in (record["paramValues"][loc]):
                        dest_record["paramValues"].append({
                            "id": param_ids_to_receive[loc],
                            "value": record["paramValues"][loc]["value"]
                        })
            dest_entity_body["records"].append(dest_record)
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [
                    {
                        "id": program_status_param_id,
                        "valueId": 2
                    }
                ]
            })
        if len(origin_entity_body["records"]) > 0:
            try:
                api.create_or_update_multi_records(origin_entity_body)
            except Exception as e:
                logger.error(f'transfer_records_based_on_blocks | Customer: {customer_name} | FAILED to update origin records | Error: {e}', exc_info=True)
                return None  # None = error occurred
            else:
                if len(dest_entity_body["records"]) > 0:
                    try:
                        api.create_or_update_multi_records(dest_entity_body)
                    except Exception as e:
                        logger.error(f'transfer_records_based_on_blocks | Customer: {customer_name} | FAILED to create destination records | Error: {e}', exc_info=True)
                        return None  # None = error occurred
                    else:
                        return True
        return False


def transfer_records(customer_name, api, origin_entity_id, dest_entity_id, search_criteria, param_ids_to_transfer,
                     param_ids_to_receive, program_status_param_id, new_id_pos):
    try:
        results = api.get_records_by_search_criteria_and_params(
            entity_id=origin_entity_id,
            params=param_ids_to_transfer,
            searchCriterias=search_criteria
        )
    except Exception as e:
        logger.error(f'transfer_records | Customer: {customer_name} | FAILED to get records from entity {origin_entity_id} | Error: {e}', exc_info=True)
        return None  # None = error occurred
    
    if "records" not in results or len(results.get("records", [])) == 0:
        return False
    
    total_found = len(results["records"])
    
    dest_entity_body = {
        "entityId": dest_entity_id,
        "records": []
    }
    origin_entity_body = {
        "entityId": origin_entity_id,
        "records": []
    }
    
    invalid_count = 0
    valid_count = 0
    
    for record in results["records"]:
        if "value" not in record["paramValues"][new_id_pos]:
            invalid_count += 1
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [{
                    "id": program_status_param_id,
                    "valueId": 3,
                    "value": "נבדק - לא תקין"
                }]
            })
            continue
        elif not record["paramValues"][new_id_pos]["value"].isnumeric():
            invalid_count += 1
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [{
                    "id": program_status_param_id,
                    "valueId": 3,
                    "value": "נבדק - לא תקין"
                }]
            })
            continue
        elif (int(record["paramValues"][new_id_pos]["value"]) == 0 or
              int(record["paramValues"][new_id_pos]["value"]) < 0):
            invalid_count += 1
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [{
                    "id": program_status_param_id,
                    "valueId": 3,
                    "value": "נבדק - לא תקין"
                }]
            })
            continue
        else:
            valid_count += 1
            new_record_id = int(record["paramValues"][new_id_pos]["value"])
            dest_record = {
                "recordId": new_record_id,
                "paramValues": []
            }
            for loc in range(len(param_ids_to_transfer)):
                if "value" in (record["paramValues"][loc]) and "valueId" in (record["paramValues"][loc]):
                    dest_record["paramValues"].append({
                        "id": param_ids_to_receive[loc],
                        "value": record["paramValues"][loc]["value"],
                        "valueId": record["paramValues"][loc]["valueId"]
                    })
                    continue
                if "value" in (record["paramValues"][loc]):
                    dest_record["paramValues"].append({
                        "id": param_ids_to_receive[loc],
                        "value": record["paramValues"][loc]["value"]
                    })
            dest_entity_body["records"].append(dest_record)
            origin_entity_body["records"].append({
                "recordId": record["recordId"],
                "paramValues": [
                    {
                        "id": program_status_param_id,
                        "valueId": 2
                    }
                ]
            })
    
    if len(origin_entity_body["records"]) > 0:
        try:
            api.create_or_update_multi_records(origin_entity_body)
        except Exception as e:
            logger.error(f'transfer_records | Customer: {customer_name} | FAILED to update origin records | Error: {e}', exc_info=True)
            return None  # None = error occurred
        else:
            if len(dest_entity_body["records"]) > 0:
                try:
                    api.create_or_update_multi_records(dest_entity_body)
                except Exception as e:
                    logger.error(f'transfer_records | Customer: {customer_name} | FAILED to create destination records | Error: {e}', exc_info=True)
                    return None  # None = error occurred
                else:
                    return True
            else:
                return True
    
    return False
