import requests
from lxml import etree
import lxml.html
from lxml import html

#this method will return xpath value
def get_value_from_xpath(node,xpath):
    try:
        value = node.xpath(xpath)[0]
    except:
        value = ""
    return value

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

#connecting to database
conn = sqlite3.connect('capriole.db')
cur = conn.cursor()

tablename = "top_100_richest_bitcoin_addresses"
headers = {
    'authority': 'bitinfocharts.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    'sec-ch-ua-mobile': '?0',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '_ga=GA1.2.1731328869.1627709784; _gid=GA1.2.1078767596.1627709784; _xicah=807b6d49-b811aa00; __gads=ID=5627c4093b273e7e:T=1627709788:S=ALNI_MZBQTZrfzFqeQpFCiWlGBr2_0ZB5Q',
    'if-modified-since': 'Sat, 31 Jul 2021 11:10:16 GMT',
}
proxies = get_proxy()
response = requests.get('https://bitinfocharts.com/top-100-richest-bitcoin-addresses.html', headers=headers, proxies=proxies)
tree = html.fromstring(response.content)

nodes = tree.xpath("//table[contains(@id,'tblOne')]//tr")

array = []
conn.execute('create table if not exists '+tablename +' ('+ keys+')')
cur.execute("DELETE FROM " + tablename )
keys = 'address,balance,coins,first_in,last_in,ins,first_out,last_out,outs'
question_marks = ','.join(list('?'*9))
for nd in nodes[1:]:
        address = get_value_from_xpath(nd,"./td/a/@href").split("/")[-1]
        balance = get_value_from_xpath(nd,"./td[position()=3]/text()")
        coins = get_value_from_xpath(nd,"./td[position()=4]/text()")
        first_in = get_value_from_xpath(nd,"./td[position()=5]/text()")
        last_in = get_value_from_xpath(nd,"./td[position()=6]/text()")
        ins = get_value_from_xpath(nd,"./td[position()=7]/text()")
        first_out = get_value_from_xpath(nd,"./td[position()=8]/text()")
        last_out = get_value_from_xpath(nd,"./td[position()=9]/text()")
        outs = get_value_from_xpath(nd,"./td[position()=last()]/text()")
        hash_val = {"address": address, "balance": balance, "coins": coins, "first_in": first_in,
               "last_in": last_in, "ins": ins, "first_out": first_out, "last_out": last_out, "outs": outs }
        keys = ','.join(hash_val.keys())
        question_marks = ','.join(list('?'*len(hash_val)))
        values = tuple(hash_val.values())
        cur.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)