import logging
from helpers import get_last_id, is_param_exists_in_entity
from datetime import datetime

# Logger configuration
logging.basicConfig(filename="log/log.txt", level=logging.DEBUG)


# Help function for internal use only
# Return a list object that contains two lists inside:
# 1. references list with all new ord requests that have no reference for next process to create records in entity 44
# 2. ord_file_records to update entity 34 with status 'waiting for reference'
# TODO: need to update the last_id after alex upgrade that no need to pass id to new records.
def prepare_references(ord_file_entity, now):
    setup_ord = {
        "references": {},
        "ord_file_records": []
    }
    for record in ord_file_entity["records"]:
        if str(record["paramValues"][1]["value"]) + str(record["paramValues"][2]["value"]) + now not in setup_ord[
            "references"]:
            setup_ord["references"][
                str(record["paramValues"][1]["value"]) + str(record["paramValues"][2]["value"]) + now] = {
                "count": 1,
                "sapak": str(record["paramValues"][1]["value"]),
                "date": str(record["paramValues"][2]["value"]),
                "now": now
            }
        else:
            setup_ord["references"][
                str(record["paramValues"][1]["value"]) + str(record["paramValues"][2]["value"]) + now]["count"] += 1
        setup_ord["ord_file_records"].append({"recordId": record["paramValues"][0]["value"], "paramValues": [
            {"id": 691, "value": "נשלחה בקשה לאסמכתא", "valueId": 8}, {"id": 692, "value": now}]})
    return setup_ord


class OrdFunctions:
    def __init__(self, api):
        self.api = api
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- START Initialize ORD Function '
            f'-----------------!')

    # Check for new records in entity 34 (ordfile)
    # If there is a record without reference it will change the status to 'waiting for reference'
    # If there is a record with reference it will change the status to 'ready to validate'
    # If no new records nothing will happen
    def check_for_new_ord_rows(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 - START ---'
            f'--------------!')
        try:
            ord_file_entity = self.api.get_records_by_search_criteria_and_params(
                entity_id=34,
                params=[472, 477, 691],
                searchCriterias=[
                    {
                        "paramId": 691,
                        "operator": "E"
                    }
                ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 - '
                f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 34  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in ord_file_entity:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 - END '
                f'WITH NO NEW ORD ROWS  -----------------!')
            return
        body = {
            "entityId": 34,
            "records": []
        }
        for record in ord_file_entity["records"]:
            if record["paramValues"][0].get("value") is None:
                body["records"].append(
                    {
                        "recordId": record["recordId"],
                        "paramValues": [
                            {
                                "id": 477,
                                "value": "ממתין לאסמכתא",
                                "valueId": 6
                            },
                            {
                                "id": 691,
                                "value": "ממתין לאסמכתא",
                                "valueId": 2
                            }
                        ]
                    })
            else:
                body["records"].append(
                    {
                        "recordId": record["recordId"],
                        "paramValues": [
                            {
                                "id": 477,
                                "value": "בקשה חדשה",
                                "valueId": 1
                            },
                            {
                                "id": 691,
                                "value": "מוכן לולידציה",
                                "valueId": 3
                            }
                        ]
                    })
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 -'
                f' TRY TO UPDATE RECORDS {body} -----------------!')
            self.api.create_or_update_multi_records(body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 -'
                f' END WITH ERRORS TRYING TO UPDATE {body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_34 -'
                f' END SUCCESSFULLY -----------------!')

    # Check for records that need to update reference number
    # Create new row in entity 44 (TEMPORDDATES) in status waiting for reference
    # This status fire up a Hito process to the relevent user by the customer code
    def ord_temp_reference(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference - START ---'
            f'--------------!')
        try:
            ord_file_entity = self.api.get_records_by_search_criteria_and_params(
                entity_id=34,
                params=[470, 471, 473, 691],
                searchCriterias=[
                    {
                        "paramId": 691,
                        "operator": "EQ",
                        "values": ["2"]
                    }
                ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference - END WITH ERRORS'
                f'COULD NOT GET RECORDS FROM ENTITY 34  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        else:
            if "records" not in ord_file_entity:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference - END '
                    f'WITH NO NEW REFERENCES  -----------------!')
                return
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp_ord_dates_body = {
                "entityId": 44,
                "records": []
            }
            setup_ord = prepare_references(ord_file_entity, now)
            ord_file_body = {
                "entityId": 34,
                "records": setup_ord["ord_file_records"]
            }
            try:
                last_id = get_last_id(self.api, 44, 611)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference - END WITH ERRORS'
                    f'COULD NOT GET LAST ID  -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference - '
                    f'ERROR MESSAGE {e} -----------------!')
                return
            for reference in setup_ord["references"]:
                temp_ord_dates_body["records"].append({"recordId": last_id, "paramValues": [
                    {"id": 612, "value": setup_ord["references"][reference]["sapak"]},
                    {"id": 614, "value": setup_ord["references"][reference]["date"]},
                    {"id": 616, "value": setup_ord["references"][reference]["count"]},
                    {"id": 703, "value": now},
                    {"id": 617, "value": "ממתין לאסמכתא", "valueId": 1}]})
                last_id += 1
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                    f' TRY TO UPDATE RECORDS {temp_ord_dates_body} -----------------!')
                self.api.create_or_update_multi_records(temp_ord_dates_body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                    f' END WITH ERRORS TRYING TO UPDATE {temp_ord_dates_body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                    f' ERROR MESSAGE {e} -----------------!')
                return
            else:
                try:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                        f' TRY TO UPDATE RECORDS {ord_file_body} -----------------!')
                    self.api.create_or_update_multi_records(ord_file_body)
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                        f' END WITH ERRORS TRYING TO UPDATE {ord_file_body} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                        f' ERROR MESSAGE {e} -----------------!')
                    return
                else:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- ord_temp_reference -'
                        f' END SUCCESSFULLY -----------------!')

    # This function checks for new references in entity 44
    # If there is new reference it transfer the reference number to entity 34
    # It also changes the status in entity 44 to 'reference transferred'
    # In entity 34 it changes the program status to 'ready for validation' and chemipal status to 'new request'
    def check_for_new_reference(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference - START ---'
            f'--------------!')
        try:
            ord_temp_entity = self.api.get_record_by_search_criterias(
                entity_id=44,
                searchCriterias=[
                    {
                        "paramId": 617,
                        "operator": "EQ",
                        "values": ["2"]
                    }
                ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference - END WITH ERRORS'
                f'COULD NOT GET RECORDS FROM ENTITY 44  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" in ord_temp_entity:
            ord_file_body = {
                "entityId": 34,
                "records": []
            }
            ord_temp_body = {
                "entityId": 44,
                "records": []
            }
            for record in ord_temp_entity["records"]:
                try:
                    ord_file_entity = self.api.get_records_by_search_criteria_and_params(
                        entity_id=34,
                        params=[472],
                        searchCriterias=[
                            {
                                "paramId": 471,
                                "operator": "EQ",
                                "values": [record["paramValues"][1].get("value")]
                            },
                            {
                                "paramId": 473,
                                "operator": "EQ",
                                "values": [record["paramValues"][2].get("value")]
                            },
                            {
                                "paramId": 692,
                                "operator": "EQ",
                                "values": [record["paramValues"][6].get("value")]
                            }
                        ])
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                        f' END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 34  -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference - '
                        f'ERROR MESSAGE {e} -----------------!')
                    return
                ord_temp_body["records"].append({
                    "recordId": record["recordId"],
                    "paramValues": [
                        {
                            "id": 617,
                            "value": "אסמכתא הועבר בהצלחה",
                            "valueId": 3
                        }
                    ]
                })
                for ord_file_record in ord_file_entity["records"]:
                    ord_file_body["records"].append(
                        {
                            "recordId": ord_file_record["recordId"],
                            "paramValues": [
                                {
                                    "id": 472,
                                    "value": record["paramValues"][3].get("value")
                                },
                                {
                                    "id": 691,
                                    "value": "מוכן לולידציה",
                                    "valueId": 3
                                },
                                {
                                    "id": 477,
                                    "value": "בקשה חדשה",
                                    "valueId": 1
                                }
                            ]
                        })
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                    f' TRY TO UPDATE RECORDS {ord_file_body} -----------------!')
                self.api.create_or_update_multi_records(ord_file_body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                    f' END WITH ERRORS TRYING TO UPDATE {ord_file_body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                    f' ERROR MESSAGE {e} -----------------!')
                return
            else:
                try:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                        f' TRY TO UPDATE RECORDS {ord_temp_body} -----------------!')
                    self.api.create_or_update_multi_records(ord_temp_body)
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                        f' END WITH ERRORS TRYING TO UPDATE {ord_temp_body} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                        f' ERROR MESSAGE {e} -----------------!')
                    return
                else:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference -'
                        f' END SUCCESSFULLY -----------------!')
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_reference - END '
                f'WITH NO NEW REFERENCES  -----------------!')
            return

    # This function is validate all the rows with status ready to validate in entity 34
    # Rows that not passed the validation will receive the appropriate status and will no longer be available to use.
    # Rows that passes the validation will get a new status "waiting for update 'askord' in inv"
    def validate_ord_rows(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - START ---'
            f'--------------!')
        try:
            ord_file_entity = self.api.get_record_by_search_criterias(entity_id=34, searchCriterias=[
                {
                    "paramId": 691,
                    "operator": "EQ",
                    "values": ["3"]
                }
            ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 34  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in ord_file_entity:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                f'END WITH NO ROWS TO VALIDATE -----------------!')
            return
        body = {
            "entityId": 34,
            "records": []
        }
        for record in ord_file_entity["records"]:
            if record["paramValues"][4].get("value") is None:
                body["records"].append({"recordId": record.get("recordId"), "paramValues": [
                    {"id": 477, "value": "לא תקין - חסר מספר משטח", "valueId": 9},
                    {"id": 691, "value": "נסגר ולא עבר ולידציה", "valueId": 7}]})
                continue
            try:
                if is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 101,
                        "operator": "EQ",
                        "values": [record["paramValues"][4].get("value")]
                    },
                    {
                        "paramId": 97,
                        "operator": "EQ",
                        "values": [record["paramValues"][1].get("value")]
                    }
                ], entity_id=10, api=self.api):
                    body["records"].append({"recordId": record.get("recordId"), "paramValues": [
                        {"id": 477, "value": "לא תקין - כבר קיימת בקשה למשטח זה", "valueId": 7},
                        {"id": 691, "value": "נסגר ולא עבר ולידציה", "valueId": 7}]})
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 101, 97,'
                    f' VALUE - {record["paramValues"][4].get("value")}'
                    f' VALUE - {record["paramValues"][1].get("value")} '
                    f'FROM ENTITY 10 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            try:
                if is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 225,
                        "operator": "EQ",
                        "values": [record["paramValues"][4].get("value")]
                    }
                ], entity_id=19, api=self.api):
                    body["records"].append({"recordId": record.get("recordId"), "paramValues": [
                        {"id": 477, "value": "לא תקין - המשטח כבר יצא מכמיפל והתקבלה תעודת משלוח", "valueId": 3},
                        {"id": 691, "value": "נסגר ולא עבר ולידציה", "valueId": 7}]})
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 225,'
                    f' VALUE - {record["paramValues"][4].get("value")}'
                    f'FROM ENTITY 19 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            try:
                if not is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 513,
                        "operator": "EQ",
                        "values": [record["paramValues"][4].get("value")]
                    },
                    {
                        "paramId": 62,
                        "operator": "EQ",
                        "values": [record["paramValues"][1].get("value")]
                    }
                ], entity_id=8, api=self.api):
                    body["records"].append({"recordId": record.get("recordId"), "paramValues": [
                        {"id": 477, "value": "לא תקין - לא קיים מספר משטח כזה במלאי", "valueId": 4},
                        {"id": 691, "value": "נסגר ולא עבר ולידציה", "valueId": 7}]})
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 513, 62,'
                    f' VALUE - {record["paramValues"][4].get("value")}'
                    f' VALUE - {record["paramValues"][1].get("value")} '
                    f'FROM ENTITY 8 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            if len(record["paramValues"][2].get("value")) > 10:
                body["records"].append({"recordId": record.get("recordId"), "paramValues": [
                    {"id": 477, "value": "לא תקין - אסמכתא גדולה מ10 תווים", "valueId": 8},
                    {"id": 691, "value": "נסגר ולא עבר ולידציה", "valueId": 7}]})
                continue
            try:
                if is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 147,
                        "operator": "EQ",
                        "values": [record["paramValues"][2].get("value")]
                    },
                    {
                        "paramId": 97,
                        "operator": "EQ",
                        "values": [record["paramValues"][1].get("value")]
                    }
                ], entity_id=10, api=self.api):
                    body["records"].append({"recordId": record.get("recordId"), "paramValues": [
                        {"id": 477, "value": "לא תקין - מספר תעודת משלוח קיים כבר", "valueId": 5},
                        {"id": 691, "value": "נסגר ולא עבר ולידציה", "valueId": 7}]})
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 147, 97,'
                    f' VALUE - {record["paramValues"][2].get("value")}'
                    f' VALUE - {record["paramValues"][1].get("value")} '
                    f'FROM ENTITY 10 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows_entity_34 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            body["records"].append(
                {
                    "recordId": record.get('recordId'),
                    "paramValues": [
                        {
                            "id": 477,
                            "value": "בקשה נשלחה לכמיפל",
                            "valueId": 2
                        },
                        {
                            "id": 691,
                            "value": "עבר ולידציה, ממתין לעדכון בINV",
                            "valueId": 9
                        }
                    ]
                })
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows entity 34 -'
                f' TRY TO UPDATE RECORDS {body} -----------------!')
            self.api.create_or_update_multi_records(body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows entity 34 -'
                f' END WITH ERRORS TRYING TO UPDATE {body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows entity 34 -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_ord_rows entity 34 -'
                f' END SUCCESSFULLY -----------------!')

    # this function updates ord rows that passed validation in askord param in entity 8 (INV)
    # after updating entity 8 the rows in ordfile will get new status 'ready for numbering'
    def update_ask_ord_in_inv(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv - START ---'
            f'--------------!')
        try:
            ord_file_records = self.api.get_records_by_search_criteria_and_params(
                entity_id=34,
                params=[471, 476],
                searchCriterias=[
                    {
                        "paramId": 691,
                        "operator": "EQ",
                        "values": ["9"]
                    }
                ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv - END WITH ERRORS'
                f'COULD NOT GET RECORDS FROM ENTITY 34  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in ord_file_records:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv - END WITH NO '
                f'NEW RECORDS -----------------!')
            return
        inv_body = {
            "entityId": 8,
            "records": []
        }
        ord_file_body = {
            "entityId": 34,
            "records": []
        }
        for ord_file_record in ord_file_records["records"]:
            try:
                inv_record = self.api.get_records_by_search_criteria_and_params(
                    entity_id=8,
                    params=[60],
                    searchCriterias=[
                        {
                            "paramId": 62,
                            "operator": "EQ",
                            "values": [ord_file_record["paramValues"][0].get("value")]
                        },
                        {
                            "paramId": 513,
                            "operator": "EQ",
                            "values": [ord_file_record["paramValues"][1].get("value")]
                        }
                    ])
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv - '
                    f'END WITH ERROR TRYING TO GET INV RECORD BASED ON CRITERIA:'
                    f' CODESAPAK - {ord_file_record["paramValues"][0].get("value")},'
                    f' REFERENCE NUMBER - {ord_file_record["paramValues"][1].get("value")} '
                    f'FROM ENTITY 8 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            if "records" in inv_record:
                inv_body["records"].append(
                    {
                        "recordId": inv_record["records"][0]["recordId"],
                        "paramValues": [
                            {
                                "id": 528,
                                "value": 1
                            }
                        ]
                    }
                )
                ord_file_body["records"].append(
                    {
                        "recordId": ord_file_record["recordId"],
                        "paramValues": [
                            {
                                "id": 691,
                                "value": "מוכן למספור",
                                "valueId": 4
                            }
                        ]
                    }
                )
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                f' TRY TO UPDATE RECORDS {inv_body} -----------------!')
            self.api.create_or_update_multi_records(inv_body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                f' END WITH ERRORS TRYING TO UPDATE {inv_body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            try:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                    f' TRY TO UPDATE RECORDS {ord_file_body} -----------------!')
                self.api.create_or_update_multi_records(ord_file_body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                    f' END WITH ERRORS TRYING TO UPDATE {ord_file_body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                    f' ERROR MESSAGE {e} -----------------!')
                return
            else:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- update_ask_ord_in_inv -'
                    f' END SUCCESSFULLY -----------------!')

