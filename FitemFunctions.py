import logging
from helpers import is_param_exists_in_entity, entity_param_2_entity_param
from datetime import datetime
from logging_config import setup_logging, get_logger

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)


class FitemFunctions:
    def __init__(self, api):
        self.api = api
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- '
            f'START Initialize FITEM Function -----------------!')

    # Check for new records in entity 28 (FITEMCHECK)
    # If there is a record it will change the status to 'ready to validate'
    # If no new records nothing will happen
    def check_for_new_fitem_rows(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_fitem_rows_entity_28 - START ---'
            f'--------------!')
        try:
            fitem_file_entity = self.api.get_records_by_search_criteria_and_params(
                entity_id=28,
                params=[342],
                searchCriterias=[
                    {
                        "paramId": 702,
                        "operator": "E"
                    }
                ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28'
                f' - END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 28  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28 - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in fitem_file_entity:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28 - END '
                f'WITH NO NEW FITEM ROWS  -----------------!')
            return
        body = {
            "entityId": 28,
            "records": []
        }
        for record in fitem_file_entity["records"]:
            body["records"].append(
                {
                    "recordId": record["recordId"],
                    "paramValues": [
                        {
                            "id": 702,
                            "value": "מוכן לולידציה",
                            "valueId": 1
                        }
                    ]
                }
            )
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28 -'
                f' TRY TO UPDATE RECORDS {body} -----------------!')
            self.api.create_or_update_multi_records(body=body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28 -'
                f' END WITH ERRORS TRYING TO UPDATE {body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28 -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            entity_param_2_entity_param(
                api=self.api,
                origin_entity_id=6,
                dest_entity_id=28,
                origin_param_id_to_find=283,
                dest_param_id_to_find=354,
                origin_param_id_to_transfer=52,
                dest_param_id_to_recieve=353
            )
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- check_for_new_rows_entity_28 - END -----------------!')
            return

    # This function is validate all the rows with status ready to validate in entity 28
    # Rows that not passed the validation will receive the appropriate status and will no longer be available to use.
    # Rows that passes the validation will get a new status 'ready to transfer' "
    def validate_fitem_rows(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - START ---'
            f'--------------!')
        try:
            fitem_check_entity = self.api.get_record_by_search_criterias(entity_id=28, searchCriterias=[
                {
                    "paramId": 702,
                    "operator": "EQ",
                    "values": ["1"]
                }
            ])
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - END WITH ERRORS'
                f'COULD NOT GET RECORDS FROM ENTITY 28  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - '
                f'ERROR MESSAGE {e} -----------------!')
            return
        if "records" not in fitem_check_entity:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - '
                f'END WITH NO ROWS TO VALIDATE -----------------!')
            return
        fitem_check_body = {
            "entityId": 28,
            "records": []
        }
        for fitem_check_record in fitem_check_entity["records"]:
            if fitem_check_record["paramValues"][7].get("value") is None or fitem_check_record["paramValues"][5].get(
                    "value") is None or fitem_check_record["paramValues"][6].get("value") is None or \
                    fitem_check_record["paramValues"][7].get("value") is None:
                fitem_check_body["records"].append({
                    "recordId": fitem_check_record.get("recordId"),
                    "paramValues": [
                        {
                            "id": 702,
                            "value": "נסגר ולא עבר ולידציה",
                            "valueId": 7
                        },
                        {
                            "id": 524,
                            "value": "חסרים פרטים להמשך ולידציה",
                            "valueId": 5
                        }
                    ]
                })
                continue
            try:
                if not is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 56,
                        "operator": "EQ",
                        "values": [fitem_check_record["paramValues"][3].get("value")]
                    }
                ], entity_id=7, api=self.api):
                    fitem_check_body["records"].append({
                        "recordId": fitem_check_record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 702,
                                "value": "נסגר ולא עבר ולידציה",
                                "valueId": 7
                            },
                            {
                                "id": 524,
                                "value": "לא תקין - לא קיים חוזה לספק זה",
                                "valueId": 3
                            }
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 56,'
                    f' VALUE - {fitem_check_record["paramValues"][3].get("value")} '
                    f'FROM ENTITY 7 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            try:
                if not is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 56,
                        "operator": "EQ",
                        "values": [fitem_check_record["paramValues"][3].get("value")]
                    },
                    {
                        "paramId": 58,
                        "operator": "EQ",
                        "values": [fitem_check_record["paramValues"][6].get("value")]
                    },
                    {
                        "paramId": 59,
                        "operator": "EQ",
                        "values": [fitem_check_record["paramValues"][7].get("value")]
                    }
                ], entity_id=7, api=self.api):
                    fitem_check_body["records"].append({
                        "recordId": fitem_check_record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 702,
                                "value": "נסגר ולא עבר ולידציה",
                                "valueId": 7
                            },
                            {
                                "id": 524,
                                "value": "לא תקין - סוג או גודל לא תקין",
                                "valueId": 4
                            }
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 56, 58, 59,'
                    f' VALUES - {fitem_check_record["paramValues"][3].get("value")}, '
                    f'{fitem_check_record["paramValues"][6].get("value")}, '
                    f'{fitem_check_record["paramValues"][7].get("value")} '
                    f'FROM ENTITY 7 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            try:
                if is_param_exists_in_entity(search_criteria=[
                    {
                        "paramId": 250,
                        "operator": "EQ",
                        "values": [fitem_check_record["paramValues"][5].get("value")]
                    }
                ], entity_id=1, api=self.api):
                    fitem_check_body["records"].append({
                        "recordId": fitem_check_record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 702,
                                "value": "נסגר ולא עבר ולידציה",
                                "valueId": 7
                            },
                            {
                                "id": 524,
                                "value": "לא תקין - קיים בFITEM",
                                "valueId": 2
                            }
                        ]
                    })
                    continue
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - '
                    f'END WITH ERROR TRYING TO GET RECORD BASED ON CRITERIA:'
                    f' PARAM_ID 250,'
                    f' VALUES - {fitem_check_record["paramValues"][5].get("value")}'
                    f'FROM ENTITY 7 -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                    f' ERROR MESSAGE {e}  -----------------!')
                return
            try:
                fitem_check_same_records = self.api.get_record_by_search_criterias(entity_id=28, searchCriterias=[
                    {
                        "paramId": 644,
                        "operator": "EQ",
                        "values": [fitem_check_record["paramValues"][5].get("value")]
                    },
                    {
                        "paramId": 524,
                        "operator": "E"
                    }
                ])
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                    f' END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY 28  -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows - '
                    f'ERROR MESSAGE {e} -----------------!')
                return
            if "records" in fitem_check_same_records:
                if len(fitem_check_same_records["records"]) > 1:
                    fitem_check_body["records"].append({
                        "recordId": fitem_check_record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 702,
                                "value": "נסגר ולא עבר ולידציה",
                                "valueId": 7
                            },
                            {
                                "id": 524,
                                "value": "לא תקין - כפילות בהכנסת מקטים",
                                "valueId": 6
                            }
                        ]
                    })
                    continue
            fitem_check_body["records"].append({
                "recordId": fitem_check_record.get("recordId"),
                "paramValues": [
                    {
                        "id": 702,
                        "value": "מוכן להעברה",
                        "valueId": 5
                    },
                    {
                        "id": 524,
                        "value": "תקין",
                        "valueId": 1
                    },
                    {
                        "id": 360,
                        "value": datetime.today().strftime("%Y-%m-%d")
                    }
                ]
            })
        try:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                f' TRY TO UPDATE RECORDS {fitem_check_body} -----------------!')
            self.api.create_or_update_multi_records(fitem_check_body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                f' END WITH ERRORS TRYING TO UPDATE {fitem_check_body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                f' ERROR MESSAGE {e} -----------------!')
            return
        else:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- validate_fitem_rows -'
                f' END SUCCESSFULLY -----------------!')
