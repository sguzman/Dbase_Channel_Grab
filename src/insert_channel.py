import datetime
import requests
import bs4
import psycopg2

fd = open('../channels.txt', 'r')

yt_base = 'https://www.youtube.com/channel/'

sql_insert_chann = 'INSERT INTO youtube.channels.channel (joined, channel_id, channel_title) VALUES (%s, %s, %s)'

connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')


def process(chan_id):
    url = yt_base + chan_id + '/about'
    req = requests.get(url)
    html_body = req.text
    soup = bs4.BeautifulSoup(html_body, 'html.parser')

    a = []
    for i in soup.findAll('span', class_='about-stat'):
        a.append(i.text)

    a[0] = chan_id

    if len(a) is 2:
        a[1] = datetime.datetime.strptime(a[1][a[1].index(' ') + 1:], '%b %d, %Y')

    if len(a) is 3:
        a[2] = datetime.datetime.strptime(a[2][a[2].index(' ') + 1:], '%b %d, %Y')
        a = [a[0], a[2]]

    a.append(soup.find('meta', property='og:title')['content'])
    a.append(soup.find('meta', property='og:description')['content'])

    return a[1], a[0], a[2]


def main():
    PostgreSQL_select_Query = "select channel_id from youtube.channels.channel"
    cursor = connection.cursor()
    cursor.execute(PostgreSQL_select_Query)
    records = cursor.fetchall()

    ignore = set()
    for i in records:
        ignore.add(i[0])

    channels = [(x[:-1] if x[-1] == '\n' else x) for x in fd.readlines()]
    for i in channels:
        if i not in ignore:
            data = process(i)
            print(data)
            cursor = connection.cursor()
            cursor.execute(sql_insert_chann, data)
            connection.commit()


main()
