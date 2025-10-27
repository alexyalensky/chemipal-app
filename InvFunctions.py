import logging
from helpers import is_param_exists_in_entity
from datetime import datetime

# Logger configuration
logging.basicConfig(filename="log/log.txt", level=logging.DEBUG)


def is_contract_valid(ctr_records):
    today = datetime.today().date()
    is_contract_not_expired = False
    if len(ctr_records["records"]) > 1:
        for ctr_record in ctr_records:
            if datetime.strptime(ctr_record["paramValues"][11].get("value"), '%Y-%m-%d').date() > today:
                is_contract_not_expired = True
    else:
        if datetime.strptime(ctr_records["records"][0]["paramValues"][11].get("value"), '%Y-%m-%d').date() > today:
            is_contract_not_expired = True
    return is_contract_not_expired


class InvFunctions:
    def __init__(self, api):
        self.api = api
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- START Initialize INV Function '
            f'-----------------!')

    # Check for new records in entity 33 (INVFILE)
    # If there is a record it will change the status to 'ready to validate'
    # If no new records nothing will happen
    def check_for_new_inv_rows(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 - START ---'
            f'--------------!')
        try:
            inv_file_entity = self.api.get_records_by_search_criteria_and_params(
                entity_id=33,
                params=[460],
                searchCriterias=[
                    {
                        "paramId": 701,
                        "operator": "E"
                    }
                ])

        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 - '
                f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 33  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in inv_file_entity:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 - END '
                f'WITH NO NEW INV ROWS  -----------------!')
            return
        body = {
            "entityId": 33,
            "records": []
        }
        for record in inv_file_entity["records"]:
            body["records"].append(
                {
                    "recordId": record["recordId"],
                    "paramValues": [
                        {"id": 701, "value": "מוכן לולידציה", "valueId": 1}
                    ]
                }
            )
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 -'
                f' TRY TO UPDATE RECORDS {body} -----------------!')
            self.api.create_or_update_multi_records(body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 -'
                f' END WITH ERRORS TRYING TO UPDATE {body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_33 -'
                f' END SUCCESSFULLY -----------------!')

    # This function is validate all the rows with status ready to validate in entity 33
    # Rows that not passed the validation will receive the appropriate status and will no longer be available to use.
    # Rows that passes the validation will get a new status 'ready to transfer' "
    def validate_inv_rows(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - START ---'
            f'--------------!')
        try:
            inv_file_entity = self.api.get_record_by_search_criterias(entity_id=33, searchCriterias=[
                {
                    "paramId": 701,
                    "operator": "EQ",
                    "values": ["1"]
                }
            ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 33  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in inv_file_entity:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                f'END WITH NO ROWS TO VALIDATE -----------------!')
            return
        inv_file_body = {
            "entityId": 33,
            "records": []
        }
        for inv_file_record in inv_file_entity["records"]:
            if inv_file_record["paramValues"][3].get("value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - אין אסמכתא",
                            "valueId": 11
                        }
                    ]
                })
                continue
            if len(inv_file_record["paramValues"][3].get("value")) > 10:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - אסמכתא גדולה מ10 תווים",
                            "valueId": 10
                        }
                    ]
                })
            try:
                if is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 72,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][3].get("value")]
                    }
                ], entity_id=8, api=self.api):
                    inv_file_body["records"].append({
                        "recordId": inv_file_record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 701,
                                "value": "נסגר ולא עבר ולידציה",
                                "valueId": 7
                            },
                            {
                                "id": 525,
                                "value": "לא תקין - מספר תעודת משלוח קיים כבר",
                                "valueId": 2
                            }
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 72,'
                    f' VALUE - {inv_file_record["paramValues"][3].get("value")} '
                    f'FROM ENTITY 8 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            if inv_file_record["paramValues"][1].get("value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - קוד ספק לא תואם",
                            "valueId": 3
                        }
                    ]
                })
                continue
            try:
                if not is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 42,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][1].get("value")]
                    }
                ], entity_id=4, api=self.api):
                    inv_file_body["records"].append({
                        "recordId": inv_file_record.get("recordId"),
                        "paramValues": [
                            {"id": 701, "value": "נסגר ולא עבר ולידציה", "valueId": 7},
                            {"id": 525, "value": "לא תקין - קוד ספק לא תואם", "valueId": 3}
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 42,'
                    f' VALUE - {inv_file_record["paramValues"][1].get("value")} '
                    f'FROM ENTITY 4 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            if inv_file_record["paramValues"][6].get("value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {"id": 701, "value": "נסגר ולא עבר ולידציה", "valueId": 7},
                        {"id": 525, "value": 'לא תקין - לא קיים מק"ט כמיפל תואם',
                         "valueId": 4}
                    ]
                })
                continue
            try:
                if not is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 16,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][1].get("value")]
                    },
                    {
                        "paramId": 49,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][6].get("value")]
                    }
                ], entity_id=1, api=self.api):
                    inv_file_body["records"].append({
                        "recordId": inv_file_record.get("recordId"),
                        "paramValues": [
                            {"id": 701, "value": "נסגר ולא עבר ולידציה", "valueId": 7},
                            {"id": 525, "value": 'לא תקין - לא קיים מק"ט כמיפל תואם',
                             "valueId": 4}
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 16, 49,'
                    f' VALUE - {inv_file_record["paramValues"][1].get("value")},'
                    f' VALUE - {inv_file_record["paramValues"][6].get("value")} '
                    f'FROM ENTITY 1 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            if inv_file_record["paramValues"][4].get("value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - סוג משטח לא תואם לפריט",
                            "valueId": 5
                        }
                    ]
                })
                continue
            try:
                if not is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 20,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][4].get("value")]
                    },
                    {
                        "paramId": 49,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][6].get("value")]
                    },
                    {
                        "paramId": 16,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][1].get("value")]
                    }
                ], entity_id=1, api=self.api):
                    inv_file_body["records"].append({
                        "recordId": inv_file_record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 701,
                                "value": "נסגר ולא עבר ולידציה",
                                "valueId": 7
                            },
                            {
                                "id": 525,
                                "value": "לא תקין - סוג משטח לא תואם לפריט",
                                "valueId": 5
                            }
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 20, 49, 16,'
                    f' VALUE - {inv_file_record["paramValues"][4].get("value")},'
                    f' VALUE - {inv_file_record["paramValues"][6].get("value")},'
                    f' VALUE - {inv_file_record["paramValues"][1].get("value")} '
                    f'FROM ENTITY 1 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            try:
                fitem_record = self.api.get_record_by_search_criterias(entity_id=1, searchCriterias=[
                    {
                        "paramId": 20,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][4].get("value")]
                    },
                    {
                        "paramId": 49,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][6].get("value")]
                    },
                    {
                        "paramId": 16,
                        "operator": "EQ",
                        "values": [inv_file_record["paramValues"][1].get("value")]
                    }
                ])
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 1  -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'ERROR MESSAGE {e} -----------------!')
                return
            if "records" not in fitem_record:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": 'לא תקין - לא קיים מק"ט כמיפל',
                            "valueId": 4
                        }
                    ]
                })
                continue
            fitem_record = fitem_record["records"][0]
            if inv_file_record["paramValues"][9].get("value") is None:
                inv_file_record["paramValues"][9]["value"] = 0
            if int(inv_file_record["paramValues"][9].get("value")) > int(fitem_record['paramValues'][18].get('value')):
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - כמות שהוכנסה גדולה יותר מהכמות בהגדרת פריט",
                            "valueId": 6
                        }
                    ]
                })
                continue
            if fitem_record["paramValues"][10].get("value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - לא הוכנס תוקף/אצווה",
                            "valueId": 7
                        }
                    ]
                })
                continue
            if fitem_record["paramValues"][10].get("value") == "4" and inv_file_record['paramValues'][7].get(
                    "value") is None and inv_file_record["paramValues"][8].get('value') is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - לא הוכנס תוקף/אצווה",
                            "valueId": 7
                        }
                    ]
                })
                continue
            if fitem_record["paramValues"][10].get("value") == "3" and inv_file_record["paramValues"][8].get(
                    "value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - לא הוכנס תוקף/אצווה",
                            "valueId": 7
                        }
                    ]
                })
                continue
            if fitem_record["paramValues"][10].get("value") == "2" and inv_file_record["paramValues"][7].get(
                    "value") is None:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - לא הוכנס תוקף/אצווה",
                            "valueId": 7
                        }
                    ]
                })
                continue
            try:
                ctr_record = self.api.get_record_by_search_criterias(entity_id=7, searchCriterias=[
                    {
                        "paramId": 56,
                        "operator": "EQ",
                        "values": [fitem_record["paramValues"][3].get("value")]
                    },
                    {
                        "paramId": 58,
                        "operator": "EQ",
                        "values": [fitem_record["paramValues"][8].get("value")]
                    },
                    {
                        "paramId": 59,
                        "operator": "EQ",
                        "values": [fitem_record["paramValues"][15].get("value")]
                    }
                ])
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 1  -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 - '
                    f'ERROR MESSAGE {e} -----------------!')
                return
            if "records" not in ctr_record:
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - אין חוזה בתוקף",
                            "valueId": 8
                        }
                    ]
                })
                continue
            if not is_contract_valid(ctr_record):
                inv_file_body["records"].append({
                    "recordId": inv_file_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 701,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 525,
                            "value": "לא תקין - אין חוזה בתוקף",
                            "valueId": 8
                        }
                    ]
                })
                continue
            inv_file_body["records"].append({
                "recordId": inv_file_record.get("recordId"),
                "paramValues": [
                    {
                        "id": 701,
                        "value": "מוכן למספור",
                        "valueId": 4
                    },
                    {
                        "id": 525,
                        "value": "תקין",
                        "valueId": 1
                    }
                ]
            })
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                f' TRY TO UPDATE RECORDS {inv_file_body} -----------------!')
            self.api.create_or_update_multi_records(inv_file_body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                f' END WITH ERRORS TRYING TO UPDATE {inv_file_body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_inv_rows_entity_33 -'
                f' END SUCCESSFULLY -----------------!')
