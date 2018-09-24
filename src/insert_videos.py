import requests
import psycopg2
import json
import os
import datetime
import traceback
import random

max_results = 50


def insert_vid_multi(conn, datas):
    cursor = conn.cursor()
    for data in datas:
        insert_vid_no_commit(cursor, data)

    conn.commit()
    cursor.close()


def insert_vid_no_commit(cursor, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.video (uploaded, chan_id, title, tags, category_id, duration, dimension, definition, caption, licensed, projection, video_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(sql_insert_chann, data)


def insert_vid(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.video (uploaded, chan_id, title, tags, category_id, duration, dimension, definition, caption, licensed, projection, video_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql_insert_chann, data)
    conn.commit()
    cursor.close()


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_vid_from_channel(channel_id, api_key):
    url = 'https://www.googleapis.com/youtube/v3/search'
    param1 = {
        'part': 'id',
        'channelId': channel_id,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key
    }
    contents = requests.get(url, params=param1).text
    return json.loads(contents)


def get_vid_from_channel_next_page(channel_id, api_key, next_page):
    url3 = 'https://www.googleapis.com/youtube/v3/search'
    param3 = {
        'part': 'id',
        'pageToken': next_page,
        'channelId': channel_id,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key
    }
    contents = requests.get(url3, params=param3).text
    return json.loads(contents)


def get_vid_pivot(channel_id, api_key, next_page):
    if next_page is None:
        return get_vid_from_channel(channel_id, api_key)
    else:
        return get_vid_from_channel_next_page(channel_id, api_key, next_page)


def get_vid(video_ids, api_key):
    video_str = ','.join(video_ids)

    url2 = 'https://www.googleapis.com/youtube/v3/videos'
    param2 = {
        'part': 'contentDetails,id,liveStreamingDetails,localizations,recordingDetails,snippet,status,topicDetails',
        'id': video_str,
        'maxResults': max_results,
        'key': api_key
    }

    contents2 = requests.get(url2, params=param2).text
    return json.loads(contents2)


def vids(channel_id, api_key):
    a = set()
    json_data = {'nextPageToken': None}

    while 'nextPageToken' in json_data:
        next_page = json_data['nextPageToken']
        json_data = get_vid_pivot(channel_id, api_key, next_page)

        items = json_data['items']
        for item in items:
            vid_id = item['id']['videoId']
            a.add(vid_id)

    return a


def select_chan(conn):
    postgresql_select_query = 'SELECT id, chan_serial FROM youtube.channels.channel ORDER BY id'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    ignore = []
    for i in records:
        ignore.append(i)

    print(len(ignore), 'channels from table')

    cursor.close()
    return ignore


def select_vids(conn, channel_id):
    postgresql_select_query = f'SELECT video_id FROM youtube.channels.video WHERE chan_id = {channel_id} ORDER BY id'
    cursor = conn.cursor()
    cursor.execute(postgresql_select_query)
    records = cursor.fetchall()

    ignore = set()
    for i in records:
        ignore.add(i[0])

    print(len(ignore), 'videos from table')

    cursor.close()
    return ignore


def get_key_or_none(obj, keys):
    try:
        obj_tmp = obj
        for key in range(len(keys)):
            obj_tmp = obj_tmp[key]
    except:
        return None


def duration(raw_str):
    raw_str = raw_str.replace('M', 'H').replace('S', 'H')[2:]
    split_str = raw_str.split('H')[:-1]

    if len(split_str) is 3:
        delta = int(split_str[0]) * 3600 + int(split_str[1]) * 60 + int(split_str[2])
    elif len(split_str) is 2:
        delta = int(split_str[0]) * 60 + int(split_str[1])
    else:
        delta = int(split_str[0])

    return datetime.timedelta(seconds=delta)


def uploaded(raw_str):
    return datetime.datetime.strptime(raw_str, "%Y-%m-%dT%H:%M:%S.%fZ")


def main():
    connection = psycopg2.connect(user='root', password='', host='127.0.0.1', port='5432', database='youtube')
    table_chans = select_chan(connection)
    random.shuffle(table_chans)

    api_key = os.environ['API_KEY']

    for chan_id in table_chans:
        try:
            print(chan_id)
            data = vids(chan_id[1], api_key)
            old_vids = select_vids(connection, chan_id[0])
            new_vids = list(data.difference(old_vids))

            datas = []
            for vid in chunks(new_vids, max_results):
                json_vids = get_vid(vid, api_key)
                for v in json_vids['items']:
                    s = v['snippet']
                    c = v['contentDetails']

                    data = [uploaded(s['publishedAt']),
                            chan_id[0],
                            s['title'],
                            s['tags'] if 'tags' in s else [],
                            int(s['categoryId']),
                            duration(c['duration']),
                            c['dimension'],
                            c['definition'],
                            bool(c['caption'].capitalize()),
                            c['licensedContent'],
                            c['projection'],
                            v['id']]
                    print(s['title'])
                    datas.append(data)

            insert_vid_multi(connection, datas)
        except Exception as e:
            print(e)
            traceback.print_exc()
            exit(1)


main()
