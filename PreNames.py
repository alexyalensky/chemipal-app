import shutil
import csv
import os
import logging
from helpers import is_param_exists_in_entity
from datetime import datetime
from logging_config import setup_logging, get_logger

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)


class PreNames:
    def __init__(self, pre_name, destination_entity, api, path, destination_path):
        self.pre_name = pre_name
        self.destination_entity = destination_entity
        self.api = api
        self.path = path
        self.destination_path = destination_path

    def check_file_already_exists(self, file):
        try:
            files = [f for f in os.listdir(self.destination_path) if os.path.isfile(os.path.join(self.destination_path, f))]
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - {e} -----------------!')
            logging.info(f'{str(datetime.today()).split(".")[0]} | Could not check if file exists in backlog')
            return False
        else:
            if file in files:
                return True
            else:
                return False

    def move_existing_file_to_duplicate_folder_and_rename(self, file):
        destination_file = os.path.join('c:\FTP_Clients\chemipal\In\duplicates', file)
        if os.path.exists(destination_file):
            base, ext = os.path.splitext(file)
            counter = 1
            new_file = f"{base}_{counter}{ext}"
            while os.path.exists(os.path.join(self.destination_path, new_file)):
                counter += 1
                new_file = f"{base}_{counter}{ext}"
            destination_file = os.path.join(self.destination_path, new_file)
        shutil.move(os.path.join(self.path, file), destination_file)

    def updateYetraCtr(self):
        ctr = self.api.get_entity_records(7)
        today = datetime.today().date()
        body = {"entityId": 7, "records": []}
        for record in ctr["records"]:
            exp_date = datetime.strptime(record["paramValues"][11].get("value"), '%Y-%m-%d').date()
            if today < exp_date:
                if "value" in record["paramValues"][12]:
                    mistahim_in = int(record["paramValues"][12].get("value"))
                else:
                    mistahim_in = 0
                if "value" in record["paramValues"][13]:
                    mistahim_out = int(record["paramValues"][13].get("value"))
                else:
                    mistahim_out = 0
                if "value" in record["paramValues"][7]:
                    ctr_mistahim = int(record["paramValues"][7].get("value"))
                else:
                    ctr_mistahim = 0
                calculated_mistahim = ctr_mistahim - (mistahim_in - mistahim_out)
                body["records"].append(
                    {
                        "recordId": record.get("recordId"),
                        "paramValues": [
                            {
                                "id": 610,
                                "value": calculated_mistahim
                            }
                        ]
                })
        if len(body["records"]) > 0:
            self.api.create_or_update_multi_records(body)

    def extract_files(self):
        csv_files = []
        path = self.path
        try:
            files = [file for file in os.listdir(path) if
                     os.path.isfile(os.path.join(path, file)) and self.pre_name.upper() in file.upper()]
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - {e} -----------------!')
            logging.info(f'{str(datetime.today()).split(".")[0]} | There is no {self.pre_name} files in dir')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERROR PRENAMES '
                f'{self.pre_name} -----------------!')
        else:
            for file in files:
                name, ext = os.path.splitext(file)
                if ".csv" == ext:
                    csv_files.append(file)
            logging.info(f'{str(datetime.today()).split(".")[0]} | There is {len(csv_files)} valid files in dir')
            return csv_files
        finally:
            return csv_files

    def move_to_other_folder(self, files):
        for file in files:
            try:
                shutil.move(self.path + '/' + file, self.destination_path)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - {e} -----------------!')
                logging.info(f'{str(datetime.today()).split(".")[0]} | Could not move file - {file} to backlog')

    def get_param_value_ids(self, number_of_params):
        param_value_ids = []
        for location in range(0, number_of_params):
            param_value_ids.append(self.api.get_specific_param_id(self.destination_entity, location))
        return param_value_ids

    def creating_body_to_update(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- START PRENAMES '
            f'creating_body_to_update {self.pre_name} -----------------!')
        files = self.extract_files()
        if len(files) < 1:
            logging.info(f'{str(datetime.today()).split(".")[0]} | THERE IS NO {self.pre_name} FILES IN FTP')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- END PRENAMES '
                f'{self.pre_name} -----------------!')
            return False
        try:
            number_of_params = len(self.api.get_entity_params(self.destination_entity))
        except Exception as e:
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - '
                         f'{e} -----------------!')
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- ERROR '
                         f'PRENAMES {self.pre_name} - COULD NOT get_entity_params -----------------!')
            return False
        body = {
            "entityId": self.destination_entity,
            "records": []
        }
        records_for_body = []
        param_values_for_body = []
        try:
            param_value_ids = self.get_param_value_ids(number_of_params)
        except Exception as e:
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - '
                         f'{e} -----------------!')
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- ERROR '
                         f'PRENAMES {self.pre_name} - COULD NOT get_param_value_ids -----------------!')
            return False
        for file in files:
            file_exists = self.check_file_already_exists(file)
            if file_exists:
                self.move_existing_file_to_duplicate_folder_and_rename(file)
                files.remove(file)
                continue
            try:
                logging.info(f'{self.path}---{file}')
                with open(f'{self.path}/{file}', encoding='UTF8') as data_file:
                    data = csv.reader(data_file)
                    first_row_flag = True
                    for row in data:
                        if first_row_flag:
                            first_row_flag = False
                            continue
                        else:
                            for param in range(0, number_of_params):
                                if param < len(row):
                                    if str(row[param]).strip() == "":
                                        continue
                                    else:
                                        param_id = str(param_value_ids[param][0]).strip()
                                        value = row[param].strip()
                                        record_id = str(row[0]).strip()
                                        record_id = int(record_id)
                                        if param_value_ids[param][1] == 'DATE':
                                            year = value[:4]
                                            month = value[4:6]
                                            day = value[6:]
                                            date = year + '-' + month + '-' + day
                                            param_values_for_body.append({'id': param_id, 'value': date})
                                        else:
                                            if param_value_ids[param][0] == 53:
                                                param_values_for_body.append({'id': param_id, 'value': int(value)})
                                            elif param_value_ids[param][0] == 55:
                                                param_values_for_body.append({'id': param_id, 'value': int(value)})
                                            elif param_value_ids[param][0] == 58:
                                                param_values_for_body.append({'id': param_id, 'value': int(value)})
                                            elif param_value_ids[param][0] == 93:
                                                param_values_for_body.append({'id': param_id, 'value': int(value)})
                                            else:
                                                param_values_for_body.append({'id': param_id, 'value': value})
                            record = {"recordId": record_id, "paramValues": param_values_for_body}
                            records_for_body.append(record)
                            param_values_for_body = []
                            logging.info(
                                f'{str(datetime.today()).split(".")[0]} | added {record} '
                                f'to body before create or update entity {self.destination_entity}')
            except Exception as e:
                logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - '
                             f'{e} -----------------!')
                logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- ERROR '
                             f'PRENAMES {self.pre_name} - COULD NOT OPEN FILE {file} -----------------!')
                continue
        body["entityId"] = self.destination_entity
        body["records"] = records_for_body
        try:
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name}'
                         f' - TRY TO UPDATE RECORDS - {body} -----------------!')
            self.api.create_or_update_multi_records(body)
        except Exception as e:
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                f' END WITH ERRORS TRYING TO UPDATE {body} -----------------!')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                f' ERROR MESSAGE {e} -----------------!')
            return False
        else:
            try:
                if len(files) > 0:
                    self.move_to_other_folder(files)
                    logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name}'
                                 f' - files {files} moved to backlog folder -----------------!')
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES '
                    f'{self.pre_name} - Could not move files to backlog -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                    f' ERROR MESSAGE {e} -----------------!')
                return False
            else:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                    f' END SUCCESSFULLY -----------------!')
                return True

    def creating_body_to_update_with_new_id(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- START PRENAMES '
            f'creating_body_to_update_with_new_id {self.pre_name} -----------------!')
        files = self.extract_files()
        if len(files) < 1:
            logging.info(f'{str(datetime.today()).split(".")[0]} | THERE IS NO {self.pre_name} FILES IN FTP')
            return
        try:
            number_of_params = len(self.api.get_entity_params(self.destination_entity))
        except Exception as e:
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - '
                         f'{e} -----------------!')
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- ERROR '
                         f'PRENAMES {self.pre_name} - COULD NOT get_entity_params -----------------!')
            return False
        body = {
            "entityId": self.destination_entity,
            "records": []
        }
        records_for_body = []
        param_values_for_body = []
        try:
            param_value_ids = self.get_param_value_ids(number_of_params)
        except Exception as e:
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - '
                         f'{e} -----------------!')
            logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- ERROR '
                         f'PRENAMES {self.pre_name} - COULD NOT get_param_value_ids -----------------!')
            return False
        else:
            for file in files:
                file_exists = self.check_file_already_exists(file)
                if file_exists:
                    self.move_existing_file_to_duplicate_folder_and_rename(file)
                    files.remove(file)
                    continue
                try:
                    logging.info(f'{self.path}---{file}')
                    with open(f'{self.path}/{file}', encoding='UTF8') as data_file:
                        data = csv.reader(data_file)
                        first_row_flag = True
                        for row in data:
                            if first_row_flag:
                                first_row_flag = False
                                continue
                            else:
                                for param in range(0, number_of_params):
                                    if param < len(row):
                                        if str(row[param]).strip() == "":
                                            continue
                                        else:
                                            param_id = str(param_value_ids[param + 1][0]).strip()
                                            value = row[param].strip()
                                            if param_value_ids[param + 1][1] == 'DATE':
                                                year = value[:4]
                                                month = value[4:6]
                                                day = value[6:]
                                                date = year + '-' + month + '-' + day
                                                param_values_for_body.append({'id': param_id, 'value': date})
                                            else:
                                                param_values_for_body.append({'id': param_id, 'value': value})
                                record = {"recordId": "auto", "paramValues": param_values_for_body}
                                records_for_body.append(record)
                                param_values_for_body = []
                                logging.info(
                                    f'{str(datetime.today()).split(".")[0]} | added {record} '
                                    f'to body before create or update entity {self.destination_entity}')
                except Exception as e:
                    logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - '
                                 f'{e} -----------------!')
                    logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- ERROR '
                                 f'PRENAMES {self.pre_name} - COULD NOT OPEN FILE {file} -----------------!')
                    continue
            body["entityId"] = self.destination_entity
            body["records"] = records_for_body
            try:
                logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name}'
                             f' - TRY TO UPDATE RECORDS - {body} -----------------!')
                self.api.create_or_update_multi_records(body)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                    f' END WITH ERRORS TRYING TO UPDATE {body} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                    f' ERROR MESSAGE {e} -----------------!')
                return False
            else:
                try:
                    if len(files) > 0:
                        self.move_to_other_folder(files)
                        logging.info(
                            f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name}'
                            f' - files {files} moved to backlog folder -----------------!')
                    logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name}'
                                 f' - files {files} moved to backlog folder -----------------!')
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES '
                        f'{self.pre_name} - Could not move files to backlog -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                        f' ERROR MESSAGE {e} -----------------!')
                    return False
                else:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name} -'
                        f' END SUCCESSFULLY -----------------!')
                    return True

    def creating_body_to_update_with_new_id_INV_FITEM(self):
        logging.info(
            f'{str(datetime.today()).split(".")[0]} | !----------------- START PRENAMES {self.pre_name} '
            f'-----------------!')
        files = self.extract_files()
        if len(files) > 0:
            try:
                number_of_params = len(self.api.get_entity_params(self.destination_entity))
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - {e} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES'
                    f' {self.pre_name} - COULD NOT GET NUMBER OF PARAMS FROM ENTITY {self.destination_entity} -----------------!')
                return False
            else:
                body = {
                    "entityId": self.destination_entity,
                    "records": []
                }
                records_for_body = []
                param_values_for_body = []
            try:
                param_value_ids = self.get_param_value_ids(number_of_params)
            except Exception as e:
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - {e} -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES '
                    f'{self.pre_name} - COULD NOT GET param_value_ids -----------------!')
                return False
            for file in files:
                file_exists = self.check_file_already_exists(file)
                if file_exists:
                    self.move_existing_file_to_duplicate_folder_and_rename(file)
                    files.remove(file)
                    continue
                try:
                    logging.info(f'{self.path}---{file}')
                    with open(f'{self.path}/{file}', encoding='UTF8') as data_file:
                        data = csv.reader(data_file)
                        first_row_flag = True
                        for row in data:
                            if first_row_flag:
                                first_row_flag = False
                                continue
                            else:
                                record_id = "auto"
                                if str(row[0]).strip() != "":
                                    record_id = str(row[0]).strip()
                                if self.pre_name == 'INV':
                                    is_exists = is_param_exists_in_entity(search_criteria=[{
                                        "paramId": int(param_value_ids[3][0]),
                                        "operator": "EQ",
                                        "values": [str(row[3].strip())]
                                    },
                                        {
                                            "paramId": int(param_value_ids[11][0]),
                                            "operator": "EQ",
                                            "values": [str(row[11].strip())]
                                        }
                                    ], entity_id=self.destination_entity, api=self.api)
                                    logging.info(f'{str(datetime.today()).split(".")[0]} | File - {file} | paramId - {param_value_ids[3][0]} | Value: {row[3]}')
                                    logging.info(f'{str(datetime.today()).split(".")[0]} | File - {file} | paramId - {param_value_ids[11][0]} | Value: {row[11]}')
                                    logging.info(f'{str(datetime.today()).split(".")[0]} | File - {file} | isExists - {is_exists}')
                                    if is_exists:
                                        continue
                                for param in range(1, number_of_params):
                                    if param < len(row):
                                        if str(row[param]).strip() == "":
                                            continue
                                        else:
                                            param_id = str(param_value_ids[param][0]).strip()
                                            value = row[param].strip()
                                            if param_value_ids[param][1] == 'DATE':
                                                year = value[:4]
                                                month = value[4:6]
                                                day = value[6:]
                                                date = year + '-' + month + '-' + day
                                                param_values_for_body.append({'id': param_id, 'value': date})
                                            else:
                                                param_values_for_body.append({'id': param_id, 'value': value})
                                record = {"recordId": record_id, "paramValues": param_values_for_body}
                                records_for_body.append(record)
                                param_values_for_body = []
                                logging.info(
                                    f'{str(datetime.today()).split(".")[0]} | added {record} to'
                                    f' body before create or update entity {self.destination_entity}')
                except Exception as e:
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS'
                        f' - {e} -----------------!')
                    logging.info(
                        f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES '
                        f'{self.pre_name} - COULD NOT OPEN FILE -----------------!')
                    continue
                else:
                    body["entityId"] = self.destination_entity
                    body["records"] = records_for_body
                    if len(body["records"]) > 0:
                        try:
                            logging.info(
                                f'{str(datetime.today()).split(".")[0]} | THE BODY TO UPDATE IS - {body}')
                            self.api.create_or_update_multi_records(body)
                            records_for_body = []
                            body["records"] = []
                        except Exception as e:
                            logging.info(
                                f'{str(datetime.today()).split(".")[0]} | !----------------- EXCEPTION IS - {e} '
                                f'-----------------!')
                            logging.info(f'{str(datetime.today()).split(".")[0]} | Could not update body! {body}')
                            logging.info(
                                f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES '
                                f'{self.pre_name} -----------------!')
                            records_for_body = []
                            body["records"] = []
                            continue
                        else:
                            logging.info(
                                f'{str(datetime.today()).split(".")[0]} | PreNames: all'
                                f' records created successfully in entity {self.destination_entity}')
                            records_for_body = []
                            body["records"] = []
                finally:
                    records_for_body = []
                    body["records"] = []
                    continue
            try:
                if len(files) > 0:
                    self.move_to_other_folder(files)
                    logging.info(f'{str(datetime.today()).split(".")[0]} | !----------------- PRENAMES {self.pre_name}'
                                 f' - files {files} moved to backlog folder -----------------!')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | files {files} moved to backlog folder')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END PRENAMES {self.pre_name} '
                    f'-----------------!')
            except Exception as e:
                logging.exception(e)
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | Could not move files to backlog')
                logging.info(
                    f'{str(datetime.today()).split(".")[0]} | !----------------- END WITH ERRORS PRENAMES '
                    f'{self.pre_name} -----------------!')
                return True
            else:
                return True
        else:
            logging.info(f'{str(datetime.today()).split(".")[0]} | THERE IS NO {self.pre_name} FILES IN FTP')
            logging.info(
                f'{str(datetime.today()).split(".")[0]} | !----------------- END PRENAMES {self.pre_name} '
                f'-----------------!')
            return False
