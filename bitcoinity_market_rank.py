import requests
import json
import datetime
import sqlite3
import random
from lxml import etree
import lxml.html
from lxml import html

#this method used to date integer to date format
def get_convert_time(val):
    timestamp = datetime.datetime.fromtimestamp(val/ 1e3)
    date = timestamp.strftime('%Y-%m-%d')
    return date

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

#this method used to return headers and data for the post request
def get_headers_and_data(url):

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'Accept': '*/*',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://data.bitcoinity.org',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': url,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = {
      'data_type': 'rank',
      'currency': 'USD',
      'exchange': 'all',
      'function': 'none',
      'timespan': '30d',
      'groups_count': '10',
      'resolution': 'hour',
      'compare': 'exchange',
      'chart_type': 'area_expanded',
      'smoothing': 'linear',
      'scale_type': 'lin'
    }
    return headers,data

#connecting to database
conn = sqlite3.connect('capriole.db')
cur = conn.cursor()
url = "https://data.bitcoinity.org/markets/rank/30d/USD?c=e&r=hour&t=ae"
headers,data = get_headers_and_data(url)
proxies = get_proxy()
tablename = "bitcoininity_market_rank"
keys = 'Exchange,volume,market_share,graph_val'
cur.execute('create table if not exists '+tablename +' ('+ keys+')')
response = requests.post('https://data.bitcoinity.org/chart_data', headers=headers, data=data, proxies=proxies)
json_val = json.loads(response.text)
aggre_additional_info = json_val["data_additional"]["aggregated"]

for val in aggre_additional_info:
    exchange = val["key"]
    for graph_hash in json_val["data"]:
        if graph_hash["key"] == exchange:
            graph_val = [{"time": get_convert_time(x[0]),"volume":x[1]} for x in graph_hash["values"]]
            question_marks = ','.join(list('?'*4))
            values = tuple([exchange,str(val["agg"]),val["share"],str(graph_val)])
            #checking data is present in the table and update it  else it will insert the data
            if cur.execute("SELECT * FROM "+tablename+" WHERE Exchange = '"+exchange+"'").fetchone():
                cur.execute('UPDATE '+tablename+' SET volume = '+str(val["agg"])+', market_share = '+val["share"]+', graph_val = "'+str(graph_val)+'"  WHERE Exchange = "'+values[0]+'"')
            else:
                cur.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
            break
        else:
            continue
data_info = json_val["info"]
export_path = json_val["export_paths"]
info_hash = {"data_point_used": data_info["total_points"], "data_point_on_chart": data_info["data_points"],
            "generated_at": get_convert_time(int(str(data_info["generated_at"])+"000")),"time_to_generate":data_info["query_time"],
            "export_path_csv":"https://data.bitcoinity.org"+json_val["export_paths"]["csv"],"export_path_xls":"https://data.bitcoinity.org"+json_val["export_paths"]["xls"]}
keys = ','.join(info_hash.keys())
question_marks = ','.join(list('?'*len(info_hash)))
values = tuple(info_hash.values())

conn.execute('create table if not exists '+tablename +'_additional ('+ keys+')')
#Deleteing old content from the table
cur.execute("DELETE FROM "+tablename+"_additional")
cur.execute('INSERT INTO '+tablename+'_additional ('+keys+') VALUES ('+question_marks+')', values)
