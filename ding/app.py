import requests
from dateutil import parser
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
from dingtk import Dingtalk_client
PHPSESSID = ""
myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['yingguang']
mycol = mydb["data"]
# db.yingguang.data.ensureIndex({"rc_id":1}, {unique:true})
page_url = 'https://www.helmenyun.cn/index.php/DataManage/data_list/{page_id}'
detail_url = 'https://www.helmenyun.cn/index.php/DataManage/data_detail'
sql = 'vendor298'
addendees = [
    "225134236032359840",
    "29671149022141745",
    "2246335848-1500630749",
    "manager4270",
    "28396364362101956772",
]

def add_slash(my_str):
    if "阴性范围" in my_str:
        substr = '阴性范围'
    elif  "参考范围" in my_str:
        substr = "参考范围"
    else:
        return my_str
    insert_txt = '\n'
    idx =  my_str.index(substr)
    my_str = my_str[:idx] + insert_txt + my_str[idx:]
    return my_str


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


headers = {

    "Cookie": "PHPSESSID=bk5ljnmepq7dasf7771v00lk34; username=Yingtianwanwu; pwd=yingtianwanwu0122",
    # "Host": "www.helmenyun.cn",
    # "Referer": "https://www.helmenyun.cn/index.php/DataManage/data_list/1",
    # "Sec-Fetch-Dest": "document",
    # "Sec-Fetch-Mode": "navigate",
    # "Sec-Fetch-Site": "same-origin",
    # "Sec-Fetch-User": "?1",
    # "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
}


# https://www.helmenyun.cn/index.php/DataManage/data_detail?sql=vendor298&SNcode=7057442a0100004e&sTime=20200714110050&RecordID=17693
# https://www.helmenyun.cn/index.php/DataManage/data_detail?sql=vendor298&SNcode=7057442a0100004e&sTime=20200714110129&RecordID=17694
def get_html(url):
    # to get the html
    # headers['Cookie'] = headers['Cookie'].format(PHPSESSID=PHPSESSID)
    # print(headers)
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    return response.text


def get_page(page_id):
    html = get_html(page_url.format(page_id=page_id))

    soup = bs(html, 'lxml')

    tbody = soup.find('tbody', {'class': 'TbodyList'})
    n_codes = tbody.find_all('td', {'class': 'check-bight'})
    n_codes = [i.input['value'] for i in n_codes]

    s_times = tbody.find_all('td', {'class': 'sTime'})
    s_times = [i.text for i in s_times]

    url_s_times = tbody.find_all('td', {'class': 'sTime'})
    url_s_times = [i.input['value'] for i in url_s_times]

    rc_ids = tbody.find_all('td', {'class': 'RecordID'})
    rc_ids = [i.text for i in rc_ids]

    jie_luns = tbody.find_all('td', {'class': 'Judge'})
    jie_luns = [i.text.strip() for i in jie_luns]
    sitem_names = tbody.find_all('td', {'class': 'sItemName'})
    sitem_names = [i.text for i in sitem_names]
            # print(sitem_names)
    return n_codes, s_times, rc_ids, jie_luns, sitem_names, url_s_times

cnt = 1
flag = True  ###
while True:
    # s = requests.session()
    # s.get('https://www.helmenyun.cn/index.php/login/index')
    # PHPSESSID= s.cookies['PHPSESSID']
    # s.close()
    msg = ''
    with open('START') as f:
        START = int(f.read())
    MAX = START
    MAX_ = MAX
    flag = True
    start_page = 1

    while flag:
        # 爬取新页面
        while True:
            try:
                n_codes, s_times, rc_ids, jie_luns, sitem_names, url_s_times = get_page(start_page)
            except:
                print("get_page_error, retrying")
                time.sleep(2)
                continue
            break
        # try:
        #     n_codes, s_times, rc_ids, jie_luns, sitem_names, url_s_times = get_page(start_page)
        # except Exception as e:
        #     print(e)
        #     response = dingTalk("time网络出错")
        #     print(response.text)
        for n_code, s_time, rc_id, jie_lun, sitem_name, url_s_time in zip(n_codes, s_times, rc_ids, jie_luns, sitem_names, url_s_times):
            if int(rc_id) > MAX:
                MAX = int(rc_id)
                    
            if jie_lun != "阴性" and   jie_lun!="阴性  / 阴性  / 阴性"  and jie_lun!="阴性 / 阴性" and jie_lun!='阴性 / 阴性  / 阴性' and jie_lun.count("阴性")!=3:
                print("page:" + str(start_page) + "rc_id:" + str(rc_id) + "START:" + str(START))
                if int(rc_id) > MAX_ - 100: #阈值

                    test_time, batch_name, gender, birth, facility, location, test_result, curve = get_detail(sql, n_code,
                                                                                                       url_s_time, rc_id)
                    test_result1 = test_result[0]
                    test_result2 = test_result[1] if len(test_result) >= 2 else ''
                    test_result3 = test_result[2] if len(test_result) >= 3 else ''
                    data = {
                            'n_code': '序列号：'+ n_code,
                            's_time': 'time：' + s_time,
                            'sitem_name': '项目名称：'+sitem_name,
                            'rc_id': '序号：'+rc_id,
                            'jie_lun': '检测结果：'+jie_lun,
                        'curve': "扫描曲线：" + curve.replace('扫描曲线：', ''),
                        'batch_name':'批次名称：'+ batch_name,
                        'facility': '设备投放地：'+facility,
                        'location': '详细地址：'+location,
                        'test_result1': add_slash(test_result1),
                        'test_result2': add_slash(test_result2),
                        'test_result3': add_slash(test_result3),
                        'test_time': parser.parse(s_time),   #2020/8/11 
                    }
                    my_query = {
                        'rc_id': '序号：'+rc_id
                    }
                    x = mycol.find_one(my_query)
                    if x is None:
                        #### ding日程

                        dingtk_cli =  Dingtalk_client()
                        cal_summary = data['test_result1'] + data['test_result2'] + data['test_result3']
                        cal_location = data['location']
                        cal_description = data['curve'] + '\n' + 'http://58.87.111.39/img/{rc_id}.jpg'.format(rc_id=rc_id)
                        cal_time = parser.parse(s_time)
                        cal_time = str(int(cal_time.timestamp()))
                        dingtk_cli.set_calendar(addendees, cal_summary, location, cal_description, cal_time)
                        ###
                        msg += '\n\n\n---------------------------------------------\n\n\n'
                        msg += ' \n\n '.join([str(i) for i in data.values()])
                        msg += '\n\n![screenshot](http://58.87.111.39/img/{TABLE}_{RecordID}.png)\n\n\n'.format(
                            rc_id=rc_id)
                        msg += '\n\n\n---------------------------------------------\n\n\n'
                        try:
                            x = mycol.update_one(my_query, {'$set': data}, upsert=True)

                            print(x)
                            print("record saved")
                        except Exception as e:
                            print(e)
                            print("插入数据库出错")
                    print(rc_id)
                else:
                    flag = False
                    break
        print("MAX:" + str(MAX))
        with open('START', 'w') as f:
            f.write(str(MAX))
        start_page += 1
        time.sleep(1)
    if msg!='':
        response = dingTalk(msg)
        print(response.text)
    print("waiting 5 mins")
    time.sleep(60 * 5)  ###每隔五分钟
    cnt = cnt + 1
    #if cnt%12==0:
    #    response = dingTalk("time爬虫正在运行中...")
    #    print("爬虫运行中")
    #    print(response.text)
