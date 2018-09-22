import requests
import psycopg2
import json
import os


def insert_vid(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.video (upload, vid_title, chan_id, video_length, video_serial) VALUES (%s, %s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql_insert_chann, data)
    conn.commit()
    cursor.close()


def get_vid_from_channel(channel_id, api_key):
    url = 'https://www.googleapis.com/youtube/v3/search'
    param1 = {
        'part': 'id',
        'channelId': channel_id,
        'type': 'video',
        'key': api_key
    }
    contents = requests.get(url, params=param1).text
    return json.loads(contents)


def get_vid_from_channel_next_page(channel_id, api_key, next_page):
    url3 = 'https://www.googleapis.com/youtube/v3/search'
    param3 = {
        'part': 'id',
        'nextPage': next_page,
        'channelId': channel_id,
        'type': 'video',
        'key': api_key
    }
    contents = requests.get(url3, params=param3).text
    return json.loads(contents)


def get_vid(video_id, api_key):
    url2 = 'https://www.googleapis.com/youtube/v3/videos'
    param2 = {
        'part': 'contentDetails,id,liveStreamingDetails,localizations,recordingDetails,snippet,status,topicDetails',
        'id': video_id,
        'key': api_key
    }

    contents2 = requests.get(url2, params=param2).text
    return json.loads(contents2)


def process(channel_id, api_key):
    a = []
    json_data = get_vid_from_channel(channel_id, api_key)

    next_page = json_data['nextPageToken']
    items = json_data['items']
    for page in range(json_data['pageInfo']['totalResults']):
        print(page)
        for item in items:
            json_data2 = get_vid(item['id']['videoId'], api_key)
            print(item['id']['videoId'])
            a.append(json_data2)

        json_data = get_vid_from_channel_next_page(channel_id, api_key, next_page)
        next_page = json_data['nextPageToken']
        items = json_data['items']

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


def main():
    connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')
    table_chans = set(select_chan(connection))
    api_key = os.environ['API_KEY']

    for chan_id in table_chans:
        try:
            print(chan_id[0])
            data = process(chan_id, api_key)
        except Exception as e:
            print(e)
            exit(1)


main()
