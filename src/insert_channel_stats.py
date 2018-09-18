import datetime
import requests
import bs4

fd = open('../channels.txt', 'r')

yt_base = 'https://www.youtube.com/channel/%s'


def filter_stuff(url):
    full_url = url + '/about'
    req = requests.get(full_url)
    html_body = req.text
    soup = bs4.BeautifulSoup(html_body, 'html.parser')

    a = []
    for i in soup.findAll('span', class_='about-stat'):
        a.append(i.text)

    if len(a) is 2:
        a[0] = int(a[0][:a[0].index(' ')].replace(',', ''))
        a[1] = datetime.datetime.strptime(a[1][a[1].index(' ')+1:], '%b %d, %Y')

    if len(a) is 3:
        a[0] = int(a[0][:a[0].index(' ')].replace(',', ''))
        a[1] = int(a[1].split(' ')[2].replace(',', ''))
        a[2] = datetime.datetime.strptime(a[2][a[2].index(' ') + 1:], '%b %d, %Y')

    a.append(soup.find('img', class_='channel-header-profile-image')['title'])

    return a


def main():
    channels = [(x[:-1] if x[-1] == '\n' else x) for x in fd.readlines()]
    for i in channels:
        url = yt_base % i
        data = [
            filter_stuff(url),
            datetime.datetime.now(),
        ]
        print(data)


main()
