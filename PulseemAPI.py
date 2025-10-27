import requests


class PulseemAPI:
    def __init__(self, key):
        self.key = key
        self.HEADERS = {
            "APIKEY": key,
            "Content-Type": "application/json"
        }

    def send_sms(self, send_id, from_number, to_number, message):
        url = "https://api.pulseem.com/api/v1/SmsApi/SendSms"
        body = {
            "sendId": send_id,
            "smsSendData": {
                "fromNumber": from_number,
                "toNumberList": [to_number],
                "referenceList": ["Hito"],
                "textList": [message]
            }
        }
        response_entity = requests.post(url=url, headers=self.HEADERS, json=body, verify=False)
        response_entity.raise_for_status()
