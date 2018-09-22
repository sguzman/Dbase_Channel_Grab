import requests
import json

channel_ids = [
    'UC-lHJZR3Gqxm24_Vd_AJ5Yw'
]

api_key = 'AIzaSyA3tBWmo5SL_9zC44Rn7rWid-o0g8okjOU'

for channel_id in channel_ids:
    url = 'https://www.googleapis.com/youtube/v3/search'
    param1 = {
        'part': 'id',
        'channelId': channel_id,
        'type': 'video',
        'key': api_key
    }
    contents = requests.get(url, params=param1).text
    json_data = json.loads(contents)

    pages = json_data['pageInfo']['totalResults']
    next_page = json_data['nextPageToken']
    items = json_data['items']
    for page in range(3):
        for i in items:
            video_id = i['id']['videoId']
            url2 = 'https://www.googleapis.com/youtube/v3/videos'
            param2 = {
                'part': 'contentDetails,id,liveStreamingDetails,localizations,recordingDetails,snippet,status,topicDetails',
                'id': video_id,
                'key': api_key
            }

            contents2 = requests.get(url2, params=param2).text
            json_data2 = json.loads(contents2)
            print(json.dumps(json_data2, indent=' ', separators={',', ':'}))

        url3 = 'https://www.googleapis.com/youtube/v3/search'
        param3 = {
            'part': 'id',
            'nextPage': next_page,
            'channelId': channel_id,
            'type': 'video',
            'key': api_key
        }

        contents = requests.get(url3, params=param3).text
        json_data = json.loads(contents)
        next_page = json_data['nextPageToken']
        items = json_data['items']
