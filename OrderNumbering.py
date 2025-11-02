from datetime import datetime
import logging
from logging_config import setup_logging, get_logger

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)


class OrderNumbering:
    def __init__(self, api, entity_num, numbering_param_id, order_num_param_id, sapak_name, date_pickup,
                 status_value_id, status_param_id, searchCriteria=None):
        if searchCriteria is None:
            searchCriteria = []
        self.api = api
        self.entity_num = entity_num
        self.body = {
            "entityId": entity_num,
            "records": []
        }
        self.numbering_param_id = numbering_param_id
        self.order_num_param_id = order_num_param_id
        self.sapak_name = sapak_name
        self.date_pickup = date_pickup
        self.records_to_update = {}
        self.searchCriteria = searchCriteria
        self.status_param_id = status_param_id
        self.status_value_id = status_value_id

    def start(self):
        logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- START ORDER NUMBERING '
                     f'ENTITY {self.entity_num} -----------------!')
        try:
            filtered_orders = self.api.get_records_by_search_criteria_and_params(
                self.entity_num, [
                    self.numbering_param_id,
                    self.order_num_param_id,
                    self.sapak_name,
                    self.date_pickup
                ],
                self.searchCriteria)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- OrderNumbering '
                f'get_records_by_search_criteria_and_params from entity {self.entity_num}'
                f' - END WITH ERRORS COULD NOT GET RECORDS FROM ENTITY {self.entity_num}  -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- OrderNumbering '
                f'get_records_by_search_criteria_and_params from entity - ERROR MESSAGE {e} -----------------!')
            return
        if "records" in filtered_orders:
            for order in filtered_orders["records"]:
                if "value" in order["paramValues"][0] or "value" not in order["paramValues"][1]:
                    continue
                else:
                    if str(order["paramValues"][1]["value"]) + str(order["paramValues"][2]["value"]) + str(
                            order["paramValues"][3]["value"]) not in self.records_to_update:
                        self.records_to_update[
                            str(order["paramValues"][1]["value"]) + str(order["paramValues"][2]["value"]) + str(
                                order["paramValues"][3]["value"])] = []
                        self.records_to_update[
                            str(order["paramValues"][1]["value"]) + str(order["paramValues"][2]["value"]) + str(
                                order["paramValues"][3]["value"])].append(order["recordId"])
                    else:
                        self.records_to_update[
                            str(order["paramValues"][1]["value"]) + str(order["paramValues"][2]["value"]) + str(
                                order["paramValues"][3]["value"])].append(order["recordId"])
            if self.records_to_update:
                for data in self.records_to_update:
                    numbering = 1
                    for record_to_update in self.records_to_update[data]:
                        self.body["records"].append({
                            "recordId": record_to_update,
                            "paramValues": [
                                {
                                    "id": self.numbering_param_id,
                                    "value": numbering
                                },
                                {
                                    "id": self.status_param_id,
                                    "value": "מוכן להעברה",
                                    "valueId": self.status_value_id
                                }
                            ]
                        })
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | Hito Id#{record_to_update} | Row num {numbering}')
                        numbering += 1

            if len(self.body["records"]) > 0:
                try:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- OrderNumbering -'
                        f' TRY TO UPDATE RECORDS {self.body} -----------------!')
                    self.api.create_or_update_multi_records(self.body)
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- OrderNumbering -'
                        f' END WITH ERRORS TRYING TO UPDATE {self.body} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- OrderNumbering -'
                        f' ERROR MESSAGE {e} -----------------!')
                self.body = {
                    "entityId": self.entity_num,
                    "records": []
                }
            else:
                logging.info('{str(datetime.today()).split(".")[0]} | No new orders to update')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END ORDER NUMBERING'
                    f' -----------------!')
