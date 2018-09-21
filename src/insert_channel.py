import datetime
import requests
import bs4
import psycopg2


def insert(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.channel (joined, channel_id, channel_title) VALUES (%s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql_insert_chann, data)
    conn.commit()
    cursor.close()


def title(soup):
    return soup.find('meta', property='og:title')['content']


def joined(raw_joined):
    return datetime.datetime.strptime(raw_joined[raw_joined.index(' ') + 1:], '%b %d, %Y')


def about_soup(chan_id):
    url = 'https://www.youtube.com/channel/%s/about' % chan_id
    req = requests.get(url)
    html_body = req.text

    return bs4.BeautifulSoup(html_body, 'html.parser')


def process(chan_id):
    soup = about_soup(chan_id)
    a = []
    for i in soup.findAll('span', class_='about-stat'):
        if i.text.startswith('Joined'):
            a.append(joined(i.text))

    a.append(chan_id)
    a.append(title(soup))

    return a


def select(conn):
    postgresql_select_query = "select channel_id from youtube.channels.channel"
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    ignore = set()
    for i in records:
        ignore.add(i[0])

    cursor.close()
    return ignore


def filter_chans(conn):
    ignore = select(conn)
    readlines_set = set([(x[:-1] if x[-1] == '\n' else x) for x in open('../channels.txt', 'r').readlines()])

    return readlines_set.difference(ignore)


def main():
    connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')
    clean_chans = filter_chans(connection)
    for i in clean_chans:
        try:
            data = process(i)
            print('Inserting channel', data[2])
            insert(connection, data)
        except Exception as e:
            print(str(e))


main()
