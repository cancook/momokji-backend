import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import argparse
import pandas as pd
import sqlalchemy as sa
from slack_sdk import WebClient
from django.db import IntegrityError
from sshtunnel import SSHTunnelForwarder
from googleapiclient.discovery import build

from youtube.models import YouTube


class YouTubes():
    def __init__(self):
        DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
        YOUTUBE_API_SERVICE_NAME='youtube'
        YOUTUBE_API_VERSION='v3'
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    def paik_jong_won(self):
        response_channel = self.youtube.search().list(
            channelId="UCyn-K7rZLXjGl7VXGweIlcA", # 채널 검색
            part="snippet",
            maxResults=50,
        ).execute()

        channel_id = response_channel['items'][0]['snippet']['channelId']

        video_list = []
        playlists = self.youtube.playlists().list(
            channelId=channel_id,
            part='snippet',
            maxResults=20
        ).execute()

        # * 내가 필요한 쿠킹로그 데이터는 [10] 에 위치해 있다.
        cooking_log_ids = playlists['items'][10]['id']

        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=cooking_log_ids,
            maxResults=50
        )
        next_page = True

        while next_page:
            response = request.execute()
            data = response['items']

            for video in data:
                video_id = video['contentDetails']['videoId']
                # * video_id 를 중복없이 video_list 에 삽입한다.
                if video_id not in video_list:
                    video_list.append(video_id)

            # Do we have more pages?
            if 'nextPageToken' in response.keys():
                next_page = True
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=cooking_log_ids,
                    pageToken=response['nextPageToken'], # * google-api-python-client 에서 지원하는 nextPageToken
                    maxResults=50
                )
            else:
                next_page = False # * 'nextPageToken' in response.keys() 가 없다면 End

        stats_list = []

        # * 0~50 까지의 데이터를 가져온다. 323개의 데이터 까지 6번 반복
        for i in range(0, len(video_list), 50):
            response_videos = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_list[i:i+50]
            ).execute()
            # ! 백종원
            for video in response_videos['items']:
                url_pk=video['id']
                channel_id=video['snippet']['channelId'] # 'UCyn-K7rZLXjGl7VXGweIlcA'
                title=video['snippet']['title']
                description=video['snippet']['description']
                thumbnails=video['snippet']['thumbnails']['high']
                view_count=video['statistics'].get('viewCount',0)
                like_count=video['statistics'].get('likeCount',0)
                published=video['snippet']['publishedAt']
                stats_dict=dict(url_pk=url_pk, channel_id=channel_id, title=title, description=description, thumbnails=thumbnails, published=published, view_count=view_count, like_count=like_count)
                stats_list.append(stats_dict)

        df=pd.DataFrame(stats_list)
        df.to_csv("/home/ubuntu/code/self-dining-backend/csv/백종원_쿠킹로그.csv", index=False)

        obj_list = [YouTube(**data) for data in stats_list] # YouTube(**data) YouTube Object = ORM
        try:
            YouTube.objects.bulk_create(obj_list, ignore_conflicts=True)
            count = YouTube.objects.filter(channel_id='UCyn-K7rZLXjGl7VXGweIlcA').count()
            client.chat_postMessage(
                channel="youtube",
                text=f"백종원 데이터를 가져오는데 성공했습니다.\n현제 데이터: {count} :tada: "
            )
        except IntegrityError:
            client.chat_postMessage(
                channel="youtube", 
                text=f"백종원 데이터를 가져오는데 실패했습니다.\n현제 데이터: {count} :red_circle: "
            )


    def simple_cooking(self):
        stats_dict = {}
        stats_list = []
        next_page_token = None
        
        while True:
            res = self.youtube.search().list(
                part='id',
                channelId='UCC9pQY_uaBSa0WOpMNJHbEQ',
                maxResults=50,
                pageToken=next_page_token,
                type='video'
            ).execute()
            
            video_ids = []
            for item in res['items']:
                video_ids.append(item['id']['videoId'])
            
            # API를 사용하여 동영상의 정보를 가져옵니다.
            video_details_res = self.youtube.videos().list(
                part='id,snippet,statistics',
                id=','.join(video_ids),
                maxResults=50,
            ).execute()
            # ! 자취요리신
            for video in video_details_res['items']:
                url_pk=video['id']
                channel_id=video['snippet']['channelId'] # 'UCC9pQY_uaBSa0WOpMNJHbEQ'
                title=video['snippet']['title']
                description=video['snippet']['description']
                thumbnails=video['snippet']['thumbnails']['high']
                view_count=video['statistics'].get('viewCount',0)
                like_count=video['statistics'].get('likeCount',0)
                published=video['snippet']['publishedAt']
                stats_dict=dict(url_pk=url_pk, channel_id=channel_id, title=title, description=description, thumbnails=thumbnails, published=published, view_count=view_count, like_count=like_count)
                stats_list.append(stats_dict)
            
            next_page_token = res.get('nextPageToken')
            
            if next_page_token is None:
                break

        df=pd.DataFrame(stats_list)
        df.to_csv("/home/ubuntu/code/self-dining-backend/csv/자취요리신.csv", index=False)

        obj_list = [YouTube(**data) for data in stats_list] # YouTube(**data) YouTube Object = ORM
        try:
            YouTube.objects.bulk_create(obj_list, ignore_conflicts=True)
            count = YouTube.objects.filter(channel_id='UCC9pQY_uaBSa0WOpMNJHbEQ').count()
            client.chat_postMessage(
                channel="youtube",
                text=f"자취요리신 데이터를 가져오는데 성공했습니다.\n현제 데이터: {count} :tada: "
            )
        except IntegrityError:
            client.chat_postMessage(
                channel="youtube", 
                text=f"자취요리신 데이터를 가져오는데 실패했습니다.\n현제 데이터: {count} :red_circle: "
            )


if __name__ == '__main__':
    slack_token = os.getenv('SLACK_TOKEN')
    client = WebClient(token=slack_token)

    parser = argparse.ArgumentParser(description='you must choose 백종원 and 자취요리신')
    parser.add_argument('-c', '--channel')
    args = parser.parse_args()

    y = YouTubes()

    if args.channel == '백종원':
        y.paik_jong_won()
    elif args.channel == '자취요리신':
        y.simple_cooking()
