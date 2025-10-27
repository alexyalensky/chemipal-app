import logging
from datetime import datetime


class check_volunteer_exists:

    def __init__(self, client_name, client_api, volunteering_entity, volunteers_entity, param_ids_to_transfer,
                 param_ids_to_receive,
                 volunteering_param_id, volunteer_param_id, volunteer_id_location, param_id_status_volunteer,
                 param_id_status_volunteering):
        self.client_name = client_name
        self.client_api = client_api
        self.volunteering_entity = volunteering_entity
        self.volunteers_entity = volunteers_entity
        self.param_ids_to_transfer = param_ids_to_transfer
        self.param_ids_to_receive = param_ids_to_receive
        self.volunteering_param_id = volunteering_param_id
        self.volunteer_param_id = volunteer_param_id
        self.volunteer_id_location = volunteer_id_location
        self.param_id_status_volunteer = param_id_status_volunteer
        self.param_id_status_volunteering = param_id_status_volunteering
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- START Initialize check_volunteer_exists '
            f'-----------------!')

    def get_volunteer_record(self, volunteer_record):
        record = {
            "recordId": "",
            "paramValues": []
        }
        for loc in range(len(self.param_ids_to_transfer)):
            if loc == 0:
                for param in volunteer_record["paramValues"]:
                    if self.param_ids_to_transfer[loc] == param["id"]:
                        record["recordId"] = int(param["value"])
                        break
            for param in volunteer_record["paramValues"]:
                if "value" in param and "valueId" in param and self.param_ids_to_transfer[loc] == param["id"]:
                    record["paramValues"].append(
                        {
                            "id": self.param_ids_to_receive[loc],
                            "value": param["value"].strip(),
                            "valueId": param["valueId"]
                        }
                    )
                    break
                elif "value" in param and self.param_ids_to_transfer[loc] == param["id"]:
                    record["paramValues"].append(
                        {
                            "id": self.param_ids_to_receive[loc],
                            "value": param["value"].strip()
                        }
                    )
                    break
        return record

    def start(self):
        body_volunteering_entity = {
            "entityId": self.volunteering_entity,
            "records": []
        }
        body_volunteers_entity = {
            "entityId": self.volunteers_entity,
            "records": []
        }
        ids_to_check = {}
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - {self.client_name} | START VOLUNTEER PROCEDURE')
        try:
            volunteers_from_volunteering_entity = self.client_api.get_record_by_search_criteria(
                self.volunteering_entity,
                self.volunteering_param_id,
                "EQ", ["1"])
        except Exception as e:
            logging.debug(f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - {self.client_name} | Exception - {e}')
            logging.debug(
                f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - {self.client_name} '
                f'| ERROR TRYING TO GET VOLUNTEERS FROM ENTITY {self.volunteering_entity}')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - {self.client_name} '
                f'| ENDDED WITH ERRORS VOLUNTEER PROCEDURE')
        else:
            if "records" in volunteers_from_volunteering_entity:
                for record in volunteers_from_volunteering_entity["records"]:
                    if "value" in record["paramValues"][self.volunteer_id_location]:
                        try:
                            is_volunteer_exists = self.client_api.get_record_by_search_criteria(
                                entity_id=self.volunteers_entity,
                                param_id=self.volunteer_param_id,
                                operator="EQ",
                                value=[record["paramValues"][self.volunteer_id_location]["value"]]
                            )
                        except Exception as e:
                            body_volunteering_entity["records"].append(
                                {
                                    "recordId": record["recordId"],
                                    "paramValues": [
                                        {
                                            "id": self.param_id_status_volunteering,
                                            "valueId": 3,
                                            "value": "נבדק - תז לא תקין"
                                        }
                                    ]
                                }
                            )
                            logging.debug(
                                f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - {self.client_name} |'
                                f' Exception - {e}')
                            logging.debug(
                                f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - {self.client_name} | '
                                f'VOLUNTEER ID - {record["paramValues"][self.volunteer_id_location]["value"]} '
                                f'| ERROR TRYING TO GET VOLUNTEER DETAILS FROM ENTITY {self.volunteering_entity}')
                        else:
                            if int(record["paramValues"][self.volunteer_id_location]["value"]) == 0:
                                body_volunteering_entity["records"].append(
                                    {
                                        "recordId": record["recordId"],
                                        "paramValues": [
                                            {
                                                "id": self.param_id_status_volunteering,
                                                "valueId": 3,
                                                "value": "נבדק - תז לא תקין"
                                            }
                                        ]
                                    }
                                )
                                continue
                            elif "records" not in is_volunteer_exists and \
                                    record["paramValues"][self.volunteer_id_location]["value"] not in ids_to_check:
                                ids_to_check[record["paramValues"][self.volunteer_id_location]["value"]] = 1
                                volunteer_record = self.get_volunteer_record(record)
                                volunteer_record["paramValues"].append(
                                    {
                                        "id": self.param_id_status_volunteer,
                                        "value": "פעיל",
                                        "valueId": 1
                                    }
                                )
                                body_volunteering_entity["records"].append(
                                    {
                                        "recordId": record["recordId"],
                                        "paramValues": [
                                            {
                                                "id": self.param_id_status_volunteering,
                                                "valueId": 2
                                            }
                                        ]
                                    }
                                )
                                body_volunteers_entity["records"].append(volunteer_record)
                            else:
                                body_volunteering_entity["records"].append(
                                    {
                                        "recordId": record["recordId"],
                                        "paramValues": [
                                            {
                                                "id": self.param_id_status_volunteering,
                                                "valueId": 2
                                            }
                                        ]
                                    }
                                )
                        finally:
                            continue
                try:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- CLIENT NAME - {self.client_name} '
                        f'VOLUNTEER PROCEDURE - TRY TO UPDATE RECORDS {body_volunteers_entity} -----------------!')
                    self.client_api.create_or_update_multi_records(body_volunteers_entity)
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- CLIENT NAME - {self.client_name} '
                        f'- VOLUNTEER PROCEDURE END WITH ERRORS TRYING TO '
                        f'UPDATE {body_volunteers_entity} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- CLIENT NAME - {self.client_name}'
                        f' - VOLUNTEER PROCEDURE ERROR MESSAGE {e} -----------------!')
                    return
                else:
                    try:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- CLIENT NAME'
                            f' - {self.client_name} VOLUNTEER PROCEDURE - '
                            f'TRY TO UPDATE RECORDS {body_volunteering_entity} -----------------!')
                        self.client_api.create_or_update_multi_records(body_volunteering_entity)
                    except Exception as e:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- CLIENT NAME -'
                            f' {self.client_name} - VOLUNTEER PROCEDURE END WITH ERRORS TRYING TO '
                            f'UPDATE {body_volunteering_entity} -----------------!')
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- CLIENT NAME'
                            f' - {self.client_name} - VOLUNTEER PROCEDURE ERROR MESSAGE {e} -----------------!')
                        return
                    else:
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | CLIENT NAME - '
                            f'{self.client_name} | SUCCESSFULLY ENDDED VOLUNTEER PROCEDURE')
            else:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END VOLUNTEER PROCEDURE '
                    f'WITH NO NEW VOLUNTEERS  -----------------!')
                return

