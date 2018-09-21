import datetime
import requests
import bs4
import psycopg2


def about_soup(chan_id):
    url = 'https://www.youtube.com/channel/%s/about' % chan_id
    req = requests.get(url)
    html_body = req.text

    return bs4.BeautifulSoup(html_body, 'html.parser')


def filter_stuff(chan_id):
    soup = about_soup(chan_id)

    a = []
    for i in soup.findAll('span', class_='about-stat'):
        if i.text.endswith('subscribers'):
            tmp = i.text[:i.text.index(' ')]
            a.append(int(tmp.replace(',', '')))
        elif i.text.endswith('views'):
            tmp = i.text[i.text.index(' ') + 3:]
            tmp2 = tmp[:tmp.index(' ')]
            a.append(int(tmp2.replace(',', '')))

    if len(a) is 1:
        a.append(None)

    a.append(datetime.datetime.now())

    return [a[1], a[0], a[2]]


def select(conn):
    postgresql_select_query = 'select id, channel_id from youtube.channels.channel ORDER BY id'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    ignore = set()
    for i in records:
        ignore.add(i)

    cursor.close()
    return ignore


def insert(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.channel_stats (uploaded, video_id, title, channel_id) VALUES (%s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql_insert_chann, data)
    conn.commit()
    cursor.close()


def main():
    connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')
    channels = select(connection)
    for i in channels:
        data = [i[0]] + filter_stuff(i[1])
        insert(connection, data)
        print(data)


main()
