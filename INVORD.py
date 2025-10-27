import csv
import logging
from datetime import datetime
import os
from dotenv import load_dotenv


# Logger configuration
logging.basicConfig(filename="log/log.txt", level=logging.DEBUG)


class INVORD:
    def __init__(self, api, entity_num):
        self.api = api
        self.entity_num = entity_num

    def get_param_value_ids_names(self):
        param_value_ids = []
        for location in range(1, len(self.api.get_entity_params(self.entity_num))):
            param_value_ids.append(self.api.get_specific_param_id(self.entity_num, location))
        return param_value_ids

    def get_file_name(self):
        self.file_path = os.environ.get("CHEMIPAL_EXPORT_PATH")
        self.backup_path = os.environ.get("CHEMIPAL_EXPORT_BACKUP")
        if self.entity_num == 8:
            file_name = "INV"
        elif self.entity_num == 10:
            file_name = "ORD"
        else:
            file_name = "something-else"
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | Entity {self.entity_num} is not defined for this application, please check the entity number in the '
                f'main.py file')
        return file_name

    def check_entity_and_create_csv_file(self, data_entity, headers_for_csv):
        param_value_ids_names = self.get_param_value_ids_names()
        # Date & Time configuration
        time_now = str(datetime.today()).split(".")[0]
        # Setup file name
        file_name = self.get_file_name()
        # Checks if entity is empty or not
        try:
            records = data_entity["records"]
        except:
            logging.info(f'{str(datetime.today()).split(".")[0]} | No records found in ENTITY_{self.entity_num}')
        # Adds entity records to list
        else:
            new_record = []
            new_records = []
            last_param = self.api.get_last_param_id(self.entity_num)
            for record in records:
                for params in record["paramValues"]:
                    try:
                        if "value" in params and (params["id"], 'DATE') in param_value_ids_names:
                            new_date_string = str(params["value"]).replace('-', '')
                            new_record.append(new_date_string)
                        elif "value" in params:
                            new_record.append(params["value"].strip(" \n\r\t"))
                        else:
                            new_record.append("")
                    except Exception as e:
                        logging.info(f'{str(datetime.today()).split(".")[0]} | Error while creating the new record to csv from entity {self.entity_num}')
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | The error was in the param {params["id"]} and the value {params["value"]}')
                        logging.info(f'{str(datetime.today()).split(".")[0]} | The error was {e}')
                        new_record.append("")
                    finally:
                        if params["id"] == last_param:
                            new_records.append(new_record)
                            new_record = []
            try:
                with open(f'{self.file_path}\{file_name}.csv', 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f, delimiter=',')
                    writer.writerow(headers_for_csv)
                    writer.writerows(new_records)
                    logging.info(f'{str(datetime.today()).split(".")[0]} | ENTITY_{self.entity_num} file created at {time_now} with {len(new_records)} records')
                    logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- END EXPORT INVORD -----------------!')
            except Exception as e:
                logging.exception(e)
                logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS EXPORT INVORD -----------------!')
            try:
                new_date_name = str(datetime.today()).split(".")[0].replace(" ", "-").replace(":", "-")
                with open(f'{self.backup_path}\{file_name}-{new_date_name}.csv', 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f, delimiter=',')
                    writer.writerow(headers_for_csv)
                    writer.writerows(new_records)
            except Exception as e:
                logging.exception(e)
                logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS EXPORT INVORD TO BACKUP -----------------!')

    def start(self):
        logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- START EXPORT INVORD -----------------!')
        try:
            time_now = str(datetime.today()).split(".")[0]
            start_of_day = str(datetime.now()).split(" ")[0] + " 00:00:00"
            data = self.api.get_entity_records_between_dates(self.entity_num, start_of_day, time_now)
            headers_for_csv = self.api.get_headers(self.entity_num)
            self.check_entity_and_create_csv_file(data, headers_for_csv)
        except Exception as e:
            logging.exception(e)
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS EXPORT INVORD -----------------!')
