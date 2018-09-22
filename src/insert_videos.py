import datetime
import requests
import bs4
import psycopg2


def insert_vid(conn, data):
    sql_insert_chann = 'INSERT INTO youtube.channels.video (upload, vid_title, chan_id, video_length, video_serial) VALUES (%s, %s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql_insert_chann, data)
    conn.commit()
    cursor.close()


def process(i):
    


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

    for i in table_chans:
        try:
            data = process(i)
            print(data)
        except Exception as e:
            print(e)
            exit(1)


main()
