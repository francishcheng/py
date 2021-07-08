import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
import json
import json
import codecs
from datetime import datetime
import datetime as dt
import pathlib
from pathlib import Path
import os
import configparser
from ifyouxiao import judge_youxiao
import pymongo
current_parent_dir = pathlib.Path(__file__).parent.absolute()
CONFIG_FILE_PATH = os.path.join(current_parent_dir, 'conf.ini')
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
# TABLE = config.get('database', 'TABLE')
# DB = config.get('database', 'DB')
# client = pymongo.MongoClient('localhost')
# db = client[DB]
# table = db['Yingtianwanwu']
def is_yang(record):
    detail = record.get('detail')
    judges = ''
    for item in detail:
        judges = judges + item['Judge'] 
    if '无效' in judges:
        return 'wuxiao'
    elif '阳' in judges:
        return 'yang'
    else:
        return 'yin'
class dingTalk():
    def __init__(self):
        # self.access_token = '5bb414bbd12ccb74196b58cb21893c3a36743889dc78e0ef2a6c5d2888a631d9'
        # self.secret = 'SEC3cf584e906ff16ca465b26e7324eba304a8f18f9e88171c4e6c4afcb7cb96326'
        self.access_token = config.get('dingtalk', 'access_token')
        self.secret = config.get('dingtalk', 'secret')
    def get_params(self):
        timestamp = str(round(time.time() * 1000))
        # secret = 'SEC3cf584e906ff16ca465b26e7324eba304a8f18f9e88171c4e6c4afcb7cb96326'
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign
    def msg(self, markdown_text):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "test",
                "text": markdown_text

            },
            "at": {
                "isAtAll": False
            }
        }
        json_data = json.dumps(data)
        print(json_data)
        timestamp, sign = self.get_params()
        print(timestamp, sign)
        response = requests.post(
            url='https://oapi.dingtalk.com/robot/send?access_token={access_token}&sign={sign}&timestamp={timestamp}'.format(access_token=self.access_token, sign=sign, timestamp=timestamp), data=json_data, headers=headers)
        return response
class Handler:
    drug_number_api = '/UniversalDataInterface/DataSelect_drugNum'
    data_select_api = '/UniversalDataInterface/DataSelect_drug'
    access_token_api = '/UniversalDataInterface/validate'
    select_api = '/UniversalDataInterface/DataSelect_drug'
    drug_curve_api = '/UniversalDataInterface/DataSelect_drugCurve'
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
            json_data = json.loads(response.text, encoding='utf-8')
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

        json_data = json.dumps(form_data,)
        response = requests.request("POST", self.base_url+self.drug_number_api, data=json_data)
        if response.status_code == 200:
            json_data = json.loads(response.text, encoding='utf-8')
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
        # response.encoding='utf-8'
        if response.status_code == 200:
            json_data = json.loads(response.text, encoding='utf-8')
            if json_data['status'] == 1:
                print('get drug records {i} sucessfully:'.format(i=str(pageNum)))
                return json_data['result']['recordArray']
            else:
                print('invalid args in getting drug records')
        else:
            print('network error:', response.status_code)
    
    def get_curve(self, record_id):
        if self.access_token == '':
            print('error: has not gotten access_token yet!')
            return
        form_data = {
            "access_token" : self.access_token,
            "RecordID": str(record_id)
        }

        json_data = json.dumps(form_data)
        response = requests.request("POST", self.base_url+self.drug_curve_api, data=json_data)
        # response.encoding='utf-8'
        if response.status_code == 200:
            json_data = json.loads(response.text, encoding='utf-8')
            if json_data['status'] == 1:
                return json_data['result']['CurvePoint']
            else:
                print('invalid args in getting drug curve')
        else:
            print('network error:', response.status_code)

if __name__ == '__main__':
    dingtalk = dingTalk()

    base_url = config.get('web', 'base_url')
    post_img_url = config.get('web', 'post_img_url')

    username = config.get('web', 'username')
    password = config.get('web', 'password')

    client = pymongo.MongoClient('localhost')
    DB = config.get('database', 'DB')
    db = client[DB]
    # db = client[DB]
    # TABLE = config.get('database', 'TABLE')
    table = db[username]
    while True:  
        now = datetime.now()
        # last_day = datetime(now.year, now.month%12+1, 1)
        # first_day = datetime(now.year, now.month%12, 1)
        last_day = datetime.now() 
        # last_day = first_day + dt.timedelta(minutes=-6)
        first_day = last_day + dt.timedelta(minutes=-10)
        first_day_strf = first_day.strftime("%Y%m%d%H%M%S")
        last_day_strf = last_day.strftime("%Y%m%d%H%M%S")
        print(first_day_strf)
        print(last_day_strf)


        handler = Handler(base_url, username, password)
        handler.get_access_token()


        drug_number = handler.get_drug_number(first_day_strf, last_day_strf)
        records =  []
        previous_recordID = []
        for i in range(1,  int(drug_number)//100+2):
            records = records + handler.get_record(i, 100, first_day_strf, last_day_strf)
            time.sleep(2)
        print(len(records))
        msg = ''            
        for record in records:
            if record['RecordID'] not in previous_recordID:
                # youxiaowuxiao
                # record['points'] = "93960,93942,93916,93922,93933,93956,93974,93999,93994,93982,93952,93918,93842,93747,93620,93472,93287,93105,92921,92746,92581,\
                # 92418,92273,92139,92006,91866,91760,91651,91553,91461,91390,91294,91207,91117,91008,90880,90755,90616,90450,90300,90154,90013,89868,89733,89592,89428,\
                #     89266,89093,88910,88705,88527,88315,88104,87895,87707,87509,87331,87171,87037,86913,86816,86753,86735,86756,86837,86975,87199,87493,87865,88318,88895,\
                #         89564,90391,91386,92595,94012,95721,97748,100186,103133,106690,110986,116141,122289,129557,138144,148178,159857,173337,188731,206095,225388,246435,\
                #             268984,292692,317093,341745,366158,389839,412280,433043,451647,467695,480811,490691,497097,499898,499033,494541,486587,475360,461167,444370,425388,\
                #                 404636,382606,359760,336559,313442,290835,269125,248648,229689,212447,197043,183485,171726,161597,152930,145514,139142,133619,128817,124585,120836,\
                #                     117488,114480,111780,109368,107212,105323,103691,102286,101098,100111,99297,98629,98096,97692,97391,97189,97079,97040,97056,97135,97272,97446,97669,\
                #                         97925,98219,98543,98935,99388,99929,100571,101341,102242,103335,104665,106280,108232,110612,113475,116917,121014,125893,131661,138436,146346,155545,\
                #                             166133,178202,191827,206958,223496,241258,259964,279300,298899,318382,337378,355521,372395,387679,401020,412087,420623,426422,429359,429395,426559,\
                #                                 420933,412729,402119,389353,374769,358696,341472,323477,305101,286641,268489,250930,234274,218762,204608,191873,180639,170845,162369,155094,148871,\
                #                                     143507,138874,134851,131310,128180,125411,122951,120752,118811,117072,115535,114157,112953,111873,110950,110149,109486,108940,108523,108208,107991,107853,107784,107773,107831,107938,108108,108328,108621,108956,109365,109845,110447,111176,112123,113352,114964,117038,119702,123030,127121,132068,137929,144748,152572,161410,171220,181974,193586,205925,218833,232112,245534,258820,271708,283898,295097,305042,313527,320329,325312,328412,329541,328680,325891,321223,314750,306688,297243,286635,275170,263139,250789,238352,226070,214103,202658,191831,181778,172574,164298,156929,150497,144945,140198,136179,132808,129979,127611,125618,123915,122445,121187,120074,119122,118314,117642,117093,116665,116330,116079,115917,115811,115792,115825,115935,116085,116283,116480,116707,116912,117109,117299,117463,117576,117616,117538,117289,116869,116208,115281,114031,112439,110462,108082,105298,102146,98611,"
                points = handler.get_curve(record['RecordID'])
                print('getting points')
                record['points'] = points
                # print(points)

                Ce = 3
                C_ygz = 15242
                youxiao = judge_youxiao(record['points'], C_ygz, Ce) 
                record['youxiao'] =  '有效' if youxiao==1 else '无效'

                query = {
                'RecordID' : record['RecordID'] 
                }
                res = table.find_one(query)
                if res is None:
                    try:
                        x = table.update_one(query, {'$set':dict(record)}, upsert=True)
                    except Exception as e:
                        print(e) 
                        print("error in updating db")
                # upload image 
                data = {
                    "points":record["points"], 
                    "TABLE":  username,
                    "RecordID": record["RecordID"]
                }
                headers = {
                    'Connection': 'close',
                }
                json_data = json.dumps(data)
                response = requests.post(post_img_url, headers=headers, data=json_data)
                time.sleep(1)
                if response.status_code != 200:
                    print("cannot upload img"+ str(record['RecordID'])) 

                #
                judge = is_yang(record) 
                # if judge != "yang":
                values = []
                for key in record.keys():
                    
                    if key!='points' and  key!='detail' and key!='IDNumber' and key!='PatientName' and key!='address' and key!='nation' and key!='BaseStation':
                        values.append(record[key])
                
                msg += '\n\n\n---------------------------------------------\n\n\n'
                msg += ' \n\n '.join([str(i) for i in values])
                msg += '\n\n![screenshot](http://58.87.111.39/img/{TABLE}_{RecordID}.png)\n\n\n'.format(TABLE=username, RecordID=record['RecordID'])
                msg += ' \n\n '.join([i['sItemName']+ ' ' + i['Judge']+ '  ' + i['Concentration'] + '  ' +i['range'] for i in record['detail']])
                msg += ' \n\n '+ record['youxiao']  + '\n\n\n'
                msg += '\n\n\n---------------------------------------------\n\n\n'
                # judge      
                # judge_res = '无效, 请重新测试' if int(item['judge_res']) == 0 else '有效'
                # msg += '判断结果:' + judge_res  

                # end if judge!= "yang"
                previous_recordID.append(record['RecordID'])
        print("msg", msg)
        response = dingtalk.msg(msg)
        print(response.text)
        time.sleep(5*60)
        print('sleep for 5 min')
