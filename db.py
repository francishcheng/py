import requests
from pypinyin import lazy_pinyin
import time
from collections import defaultdict
import hmac
import hashlib
import base64
import urllib.parse
import json
import json
from datetime import datetime
import datetime as dt
import pathlib
from pathlib import Path
import os
import configparser
from app import Handler

base_url = "http://helmenyun.cn/index.php"
username = 'Yingtianwanwu'
password = 'yingtianwanwu0122'
username1 = 'Shenzhenkunteng'
password = 'kunteng123'
usernames = ['Yingtianwanwu', 'Shenzhenkunteng']

# handler = Handler(base_url, username, password)
# handler.get_access_token()
# now = datetime.now()
# last_day = datetime(now.year, now.month%12+1, 1)
# first_day = datetime(now.year - 10, now.month%12, 1)
# first_day_strf = first_day.strftime("%Y%m%d%H%M%S")
# last_day_strf = last_day.strftime("%Y%m%d%H%M%S")
# print(first_day_strf)
# print(last_day_strf)
# drug_number = handler.get_drug_number(first_day_strf, last_day_strf)
# records =  []
# mp = {}
# for i in range(1,  int(drug_number)//100+2):
# 	records = records + handler.get_record(i, 100, first_day_strf, last_day_strf)
# for record in records:
# 	# print(record)
# 	mp[record['SNcode']] = record['Location']
# 	mp[record['Location']] = record['SNcode']
# for key in mp.keys():
# 	print(key, mp[key])
# with open('SNcode_Location_{base_url}_{username}.json'.format(base_url=base_url.split('/')[2], username=username), 'w', encoding='utf-8') as f:
# 	json.dump(mp, f, ensure_ascii=False)

dt = defaultdict(set) 
sncode_dt = {} 
for username in usernames:
	with open('SNcode_Location_{base_url}_{username}.json'.format(base_url=base_url.split('/')[2], username=username), encoding='utf-8') as f:
		json_data = json.loads(f.read())
		d = dict(json_data)
		for key in d.keys():
			if key!='' and ' ' in key:
				# print(key)
				city = ''.join(lazy_pinyin(key.split()[2]))
				dt[city].add(d[key])	
				print(key)
			# if key!='' and ' ' not in key and d[key]!='' and '杭州' not in d[key] :
			# 	sncode_dt[key] = d[key]
			# 	print(key, d[key])
for key in dt.keys():
	dt[key] = list(dt[key])
with open('localtion2sncode.json', 'w', encoding='utf-8') as f:
	json.dump(dt, f, ensure_ascii=False)
