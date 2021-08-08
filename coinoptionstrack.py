import requests
import json
import datetime
import sqlite3
import random
from lxml import etree
import lxml.html
from lxml import html

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

def get_headers_and_param(url,currency):
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'Accept': 'application/json, text/plain, */*',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Origin': 'https://www.coinoptionstrack.com',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': url,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    params = (
        ('currency', currency),
        ('expired', 'false'),
        ('kind', 'option'),
    )
    return headers,params

#connecting to database
conn = sqlite3.connect('capriole.db')
cur = conn.cursor()

url = "https://www.coinoptionstrack.com/options/BTC/open-interest"
val_hash = [{"url":url,"currency":"ETH"},{"url":url,"currency":"BTC"}]
for val in val_hash:
    headers,params = get_headers_and_param(val["url"],val["currency"])
    proxies = get_proxy()
    response = requests.get('https://www.deribit.com/api/v2/public/get_instruments', headers=headers, params=params, proxies=proxies)
    json_val = json.loads(response.text)
    data = json_val["result"]
    tablename = "Coin_options_track" + val["currency"]
    keys = ','.join(data[0].keys())
    #keys = keys.replace("instrument_name","'instrument_name'")
    conn.execute('create table if not exists '+tablename +' ('+ keys+')')
    question_marks = ','.join(list('?'*len(data[0])))
    for item in data:
        values = tuple(item.values())
        item = {k: str(v) for k, v in item.items()}
        #checking data is present in the table and update it  else it will insert the data
        if cur.execute("SELECT * FROM "+tablename+" WHERE instrument_name = '"+item["instrument_name"]+"'").fetchone():
            cur.execute("UPDATE "+tablename+" SET tick_size = "+item['tick_size']+", taker_commission = "+item['taker_commission']+", strike = "+item['strike']+", settlement_period = '"+item['settlement_period']+"', quote_currency = '"+item['quote_currency']+"', option_type = '"+item['option_type']+"', min_trade_amount = "+item['min_trade_amount']+", maker_commission = "+item['maker_commission']+", kind = '"+item['kind']+"', is_active = '"+item['is_active']+"', instrument_name = '"+item['instrument_name']+"', expiration_timestamp = "+item['expiration_timestamp']+", creation_timestamp = "+item['creation_timestamp']+", contract_size = "+item['contract_size']+", block_trade_commission = "+item['block_trade_commission']+", base_currency = '"+item['base_currency']+"' WHERE instrument_name = '"+item['instrument_name']+"'")
        else:
            cur.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
            
proxies = get_proxy()
trade_response = requests.get('https://www.deribit.com/api/v2/public/get_trade_volumes', headers=headers, proxies=proxies)
tradejson_val = json.loads(trade_response.text)
data = tradejson_val["result"]
tablename = "Coin_options_track_trade_volume" 
keys = ','.join(data[0].keys())
conn.execute('create table if not exists '+tablename +' ('+ keys+')')
question_marks = ','.join(list('?'*len(data[0])))
for val in data:
    values = tuple(val.values())   
    if cur.execute("SELECT * FROM "+tablename+" WHERE currency_pair = '"+val["currency_pair"]+"'").fetchone():
        cur.execute("UPDATE "+tablename+" SET puts_volume = "+str(val["puts_volume"])+", futures_volume = "+str(val["futures_volume"])+", currency_pair = '"+val["currency_pair"]+"', calls_volume = "+str(val["calls_volume"])+"  WHERE currency_pair = '"+val["currency_pair"]+"'")
    else:
        cur.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
        
        