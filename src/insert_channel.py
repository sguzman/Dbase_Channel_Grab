import datetime
import requests
import bs4
import psycopg2


def insert_channel_into_table(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.channel (chan_serial, title, description, google_plus, thumbnail, is_paid, is_family_friendly, username, joined) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql_insert_chann, data)
    conn.commit()
    cursor.close()


def title(soup):
    title_obj = soup.select_one('meta[name="title"]')
    if title_obj is None:
        return None
    else:
        return title_obj['content']


def joined(raw_joined):
    return datetime.datetime.strptime(raw_joined[raw_joined.index(' ') + 1:], '%b %d, %Y')


def soup_from_channel(chan_id):
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


def image(soup):
    img = soup.select_one('meta[property="og:image"]')
    if img is None:
        return None
    else:
        return img['content']


def is_paid(soup):
    paid = soup.select_one('meta[itemprop="paid"]')
    if paid is None:
        return None
    else:
        return 'True' is paid['content']


def is_family(soup):
    family = soup.select_one('meta[itemprop="isFamilyFriendly"]')
    if family is None:
        return None
    else:
        return 'True' is family['content']


def gather_chan_fields(chan_id):
    soup = soup_from_channel(chan_id)
    a = []
    join_me = None

    stats = soup.findAll('span', class_='about-stat')
    for i in stats:
        if i.text.startswith('Joined'):
            join_me = joined(i.text)
            break

    a.append(chan_id)

    title_str = title(soup)
    if title_str is None:
        return None

    a.append(title_str)
    a.append(description(soup))
    a.append(google_plus(soup))
    a.append(image(soup))
    a.append(is_paid(soup))
    a.append(is_family(soup))
    a.append(username(soup))
    a.append(join_me)

    return a


def get_incumbent_chans(conn):
    postgresql_select_query = 'SELECT chan_serial FROM youtube.channels.channel ORDER BY id'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    ignore = set()
    for i in records:
        ignore.add(i[0])

    print(len(ignore), 'channels from table')

    cursor.close()
    return ignore


def chans_txt():
    return (x.rstrip('\n') for x in open('../channels.txt', 'r').readlines())


def main():
    connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')
    table_chan = get_incumbent_chans(connection)

    for i in chans_txt():
        try:
            if i not in table_chan:
                data = gather_chan_fields(i)
                if data is None:
                    print('Got None from', i)
                else:
                    print(i)
                    insert_channel_into_table(connection, data)
        except Exception as e:
            print(e)
            exit(1)


main()
