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
    return soup.select_one('meta[name="title"]')['content']


def joined(raw_joined):
    return datetime.datetime.strptime(raw_joined[raw_joined.index(' ') + 1:], '%b %d, %Y')


def about_soup(chan_id):
    url = 'https://www.youtube.com/channel/%s/about' % chan_id
    req = requests.get(url)
    html_body = req.text

    return bs4.BeautifulSoup(html_body, 'html.parser')


def google_plus(soup):
    pub = soup.select_one('link[rel="publisher"]')
    if pub is None:
        return pub
    else:
        return pub['href']


def keywords(soup):
    a = []
    for i in soup.findAll('meta', property="og:video:tag"):
        a.append(i['content'])

    return a


def username(soup):
    raw = soup.select_one('a.channel-header-profile-image-container.spf-link')
    if raw is None:
        return None
    else:
        return raw['href'].split('/')[-1]


def process(chan_id):
    soup = about_soup(chan_id)
    a = []
    for i in soup.findAll('span', class_='about-stat'):
        if i.text.startswith('Joined'):
            a.append(joined(i.text))

    a.append(chan_id)
    a.append(title(soup))
    a.append(username(soup))
    a.append('True' is soup.select_one('meta[itemprop="paid"]')['content'])
    a.append('True' is soup.select_one('meta[itemprop="isFamilyFriendly"]')['content'])
    a.append(keywords(soup))
    a.append(google_plus(soup))
    a.append(soup.select_one('meta[property="og:image"]')['content'])
    a.append(soup.select_one('meta[name="description"]')['content'])

    return a


def select(conn):
    postgresql_select_query = 'select channel_id from youtube.channels.channel ORDER BY id'
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
            print(data)
            #insert(connection, data)
        except Exception as e:
            print(str(e))
            exit(1)


main()
