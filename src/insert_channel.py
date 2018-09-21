import datetime
import requests
import bs4
import psycopg2


def insert_chan(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.channel (chan_serial, title, description, google_plus, thumbnail, is_paid, is_family_friendly, username, joined) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
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


def username(soup):
    raw = soup.select_one('a.channel-header-profile-image-container.spf-link')
    if raw is None:
        return None
    else:
        return raw['href'].split('/')[-1]


def description(soup):
    raw = soup.select_one('meta[name="description"]')
    if raw is None:
        return None
    elif len(raw['content']) is 0:
        return None
    else:
        return raw['content']


def process(chan_id):
    soup = about_soup(chan_id)
    a = []
    join_me = None
    for i in soup.findAll('span', class_='about-stat'):
        if i.text.startswith('Joined'):
            join_me = joined(i.text)
            break

    a.append(chan_id)
    a.append(title(soup))
    a.append(description(soup))
    a.append(google_plus(soup))
    a.append(soup.select_one('meta[property="og:image"]')['content'])
    a.append('True' is soup.select_one('meta[itemprop="paid"]')['content'])
    a.append('True' is soup.select_one('meta[itemprop="isFamilyFriendly"]')['content'])
    a.append(username(soup))
    a.append(join_me)

    return a


def select_chan(conn):
    postgresql_select_query = 'SELECT chan_serial FROM youtube.channels.channel ORDER BY id'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    ignore = set()
    for i in records:
        ignore.add(i)

    print(len(ignore), 'channels from table')

    cursor.close()
    return ignore


def filter_chans():
    chans = set([(x[:-1] if x[-1] == '\n' else x) for x in open('../channels.txt', 'r').readlines()])
    print(len(chans), 'channels from channels.txt')

    return chans


def main():
    connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')
    table_chan = set(x for x in select_chan(connection))

    clean_chans = filter_chans()
    for i in clean_chans:
        try:
            if i not in table_chan:
                data = process(i)
                print(data)
                insert_chan(connection, data)
        except Exception as e:
            print(e)
            exit(1)


main()
