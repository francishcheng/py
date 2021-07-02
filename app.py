import requests
import json
from datetime import datetime
import datetime as dt
# url = "http://helmenyun.cn/index.php/UniversalDataInterface/validate"

# payload = {
#     "username": "Shenzhenkunteng",
#     "password": "kunteng123"
# }
# json_data = json.dumps(payload)
# headers = {
#     'content-type': "application/x-www-form-urlencoded",
#     'cache-control': "no-cache",
#     'postman-token': "fe43c929-a196-53c2-42a9-841ad129c067"
# }

# response = requests.request("POST", url, data=json_data, headers=headers)

# print(response.text)


class Handler:
    drug_number_api = '/UniversalDataInterface/DataSelect_drugNum'
    data_select_api = '/UniversalDataInterface/DataSelect_drug'
    access_token_api = '/UniversalDataInterface/validate'
    select_api = '/UniversalDataInterface/DataSelect_drug'
    access_token = ''

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def get_access_token(self):
        form_data = {
            'username': self.username,
            'password': self.password,
        }
        json_data = json.dumps(form_data)
        response = requests.request("POST", self.base_url+self.access_token_api, data=json_data)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['status'] == 1:
                print('get token sucessfully:', json_data['result']['access_token'])
                self.access_token = json_data['result']['access_token']
            else:
                print('invalid args, plz check out password and username')
    
        else:
            print('network error:', response.status_code)

    def get_drug_number(self, sTimeStart, sTimeEnd):
        if self.access_token == '':
            print('error: has not gotten access_token yet!')
            return
        form_data = {
                "access_token" : self.access_token,
                "sTimeStart": sTimeStart,
                "sTimeEnd" : sTimeEnd, 
            }

        json_data = json.dumps(form_data)
        response = requests.request("POST", self.base_url+self.drug_number_api, data=json_data)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['status'] == 1:
                print('get drug number sucessfully:', json_data['result']['totalCount'])
                return json_data['result']['totalCount']
            else:
                print('invalid args in getting drug number')
        else:
            print('network error:', response.status_code)
    def get_record(self,pageNum, limitPageNum, sTimeStart, sTimeEnd):
        if self.access_token == '':
            print('error: has not gotten access_token yet!')
            return
        form_data = {
                "access_token" : self.access_token,
                "sTimeStart": sTimeStart,
                "sTimeEnd" :  sTimeEnd, 
                "pageNum": pageNum,
                "limitPageNum": limitPageNum,
                }
        json_data = json.dumps(form_data)
        response = requests.request("POST", self.base_url+self.data_select_api, data=json_data)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['status'] == 1:
                print('get drug records sucessfully:')
                return json_data['result']['recordArray']
            else:
                print('invalid args in getting drug records')
        else:
            print('network error:', response.status_code)
if __name__ == '__main__':
    base_url = "http://helmenyun.cn/index.php"
    username = 'Shenzhenkunteng'
    password = 'kunteng123'
    handler = Handler(base_url, username, password)
    handler.get_access_token()

    now = datetime.now()
    last_day = datetime(now.year, now.month%12+1, 1)
    first_day = datetime(now.year, now.month%12, 1)
    first_day_strf = first_day.strftime("%Y%m%d%H%M%S")
    last_day_strf = last_day.strftime("%Y%m%d%H%M%S")

    print(first_day_strf)
    print(last_day_strf)
    drug_number = handler.get_drug_number(first_day_strf, last_day_strf)
    records =  []
    for i in range(1,  int(drug_number)//100+2):
        records = records + handler.get_record(i, 100, first_day_strf, last_day_strf)
    print(len(records))