import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from bs4 import BeautifulSoup as bs
import time
import re
import json
import pymongo
from my_detail import get_detail
from datetime import datetime as dt
import datetime
def count(n_code, result_list):
    yang = 0
    wuxiao = 0
    
    for each in result_list:
     if each['n_code'] == n_code:
         location = each['location']
    #     if each['jie_lun'] == '无效':
         if '无效' in each['jie_lun']:
             wuxiao = wuxiao + 1
         elif '质检' in each['jie_lun']:
             wuxiao = wuxiao + 1
         else:
             yang = yang + 1
    return yang, wuxiao, location
def dingTalk(markdown_text):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "msgtype": "markdown",
        # "markdown": markdown,
        "markdown": {
            "title": "检测结果",
            "text": markdown_text

            # '#### 海宁天气 @150XXXXXXXX \n> 9度，西北风1级，空气良89，相对温度73%\n> ![screenshot]('
            #     'http://58.87.111.39/img/18090.png)\n> ###### 10点20分发布 [天气]('
            #     'https://www.dingalk.com) \n '
            #     '<img src="http://58.87.111.39/img/18090.png" style="background-color: #6966ff">\n'

        },
        "at": {

            "isAtAll": False
        }
    }
    json_data = json.dumps(data)
    response = requests.post(
        # https://oapi.dingtalk.com/robot/send?access_token=05befc5bf9efaf29d80cc30ee53e4e03985853864484e7ddc758bb03ff159bf9
        url='https://oapi.dingtalk.com/robot/send?access_token=05befc5bf9efaf29d80cc30ee53e4e03985853864484e7ddc758bb03ff159bf9',
        data=json_data, headers=headers)
    return response

def send():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['yingguang']
    mycol = mydb["data"]

    now = dt.now()+datetime.timedelta(days=-1)
    query = {"test_time": {"$gt":dt(now.year, now.month, now.day, 0, 0, 0),
        "$lt":dt(now.year, now.month, now.day, 23, 59, 59)}}
    result = mycol.find(query)
    result_list = result_list = [i for i in result]
    n_codes = list(set(i['n_code'] for i in result_list))
    for result in result_list:
        print(result['test_time'])
    report_list = []
    for code in n_codes:
        print(code)
        yang, wuxiao, location = count(code, result_list)
        temp_dict = {
                    "序列号": code,
                    "阳性": yang,
                    "无效": wuxiao,
                    "详细地址": location,
                }
        report_list.append(temp_dict)
        print(yang, wuxiao, location,  sep = " ")
         
    now = dt.now()

    msg = "\ntime: {year}-{month}-{day} \n".format(year=now.year, month=now.month, day=now.day)
    for each in report_list:
        msg += "\n---------------------------------------------------\n"
        for key, value in zip(each.keys(), each.values()):
            if key == "序列号":
                value = value.replace("序列号：", "")
            if key == "详细地址":
                value = value.replace ("详细地址：", "")
            msg += (key+":")
            msg += str(value)
            msg += '\n\n'
        msg += "\n---------------------------------------------------\n"
    print(msg)

    response = dingTalk(msg)
while True:
    now = dt.now()
    if now.hour == 9 and now.minute==0:
        send()
        time.sleep(61)
        
