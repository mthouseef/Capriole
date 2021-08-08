import requests
import json
import sqlite3
import random
from lxml import etree
import lxml.html
from lxml import html

#this method used to collect some free proxy from proxynova website
def get_proxy():
    proxy_url = "https://www.proxynova.com/proxy-server-list/country-in/"
    response = requests.get(proxy_url)
    tree = html.fromstring(response.content)
    port = tree.xpath("//table[contains(@id,'tbl_proxy_list')]/tbody[1]/tr/td[2]/text()")
    proxy_list = tree.xpath("//script[contains(.,'document.write')]/text()")
    proxy_list_with_port = [proxy_list[i].split("write('")[-1].split("');")[0].strip() + ":" + port[i].strip() for i in range(len(proxy_list))]
    proxies = {
      "http": "http://"+random.choice(proxy_list_with_port),
    }
    return proxies

def get_headers_and_param(url):
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'Accept': '*/*',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': url,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    params = (
        ('ppoint', '1'),
        ('currency', 'USD'),
        ('x_type', 'currency'),
    )
    return headers,params

conn = sqlite3.connect('capriole.db')
cur = conn.cursor()
url = "https://data.bitcoinity.org/markets/books/USD"
tablename = "bitcoininity_market_books"
headers,params = get_headers_and_param(url)
proxies = get_proxy()
response = requests.get('https://data.bitcoinity.org/webs_bridge/data/books', headers=headers, params=params, proxies=proxies)
json_val = json.loads(response.text)
data = json_val["bars"]
conn.execute('create table if not exists '+tablename +' ('+ keys+')')
keys = ','.join(data[0].keys())
question_marks = ','.join(list('?'*len(data[0])))
for val in data:
    val = {k: str(v) for k, v in val.items()}
    values = tuple(val.values())
    #checking data is present in the table and update it  else it will insert the data
    if cur.execute("SELECT * FROM "+tablename+" WHERE exchange = '"+val["exchange"]+"'").fetchone():
        cur.execute('UPDATE '+tablename+' SET asks = '+val["asks"]+', bids = '+val["bids"]+', currency = "'+val["currency"]+'", exchange = "'+val["exchange"]+'", spread = '+val["spread"]+'  WHERE exchange = "'+val["exchange"]+'"')
    else:
        cur.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)