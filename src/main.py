import json
import bs4
import requests

url_base = 'https://dbase.tube/chart/channels/subscribers/all?page=%s&spf=navigate'
max_page = 19084
html_doc = requests.get(url_base).text

for i in range(max_page):
    url = url_base % i
    hot_bod = requests.get(url).text
    json_blob = json.loads(hot_bod)
    html_body = json_blob['body']['spf_content']
    soup = bs4.BeautifulSoup(html_body, 'html.parser')

    for j in soup.findAll('a', class_='list__item'):
        print(j['href'])
