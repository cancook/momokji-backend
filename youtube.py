import os, re
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
django.setup()

import argparse
import pandas as pd
from slack_sdk import WebClient
from django.db import IntegrityError
from googleapiclient.discovery import build

from youtube.models import YouTube
from search.models import Ingredients


class YouTubes():
    def __init__(self):
        DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
        YOUTUBE_API_SERVICE_NAME='youtube'
        YOUTUBE_API_VERSION='v3'
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    def ingredients(self, channel_name):
        ingredient_dict = {}
        ingredient_list = []
        target_description = None

        if channel_name == '백종원':
            objs = YouTube.objects.filter(channel_id="UCyn-K7rZLXjGl7VXGweIlcA").values_list('url_pk', 'description')
        elif channel_name == '자취요리신':
            objs = YouTube.objects.filter(channel_id="UCC9pQY_uaBSa0WOpMNJHbEQ").values_list('url_pk', 'description')

        for obj in objs:
            description = obj[1].split("\n")
            url_pk = obj[0]
            for ingredient in description:
                if '[ 재료 ]' in ingredient or '[재료]' in ingredient:
                    target_description = ingredient
                    if target_description:
                        index = description.index(target_description)
                        for i in range(index+1, len(description)):
                            #! description 의 내부 로직을 들면서 특정 문자열이 나온다면 break 해서 재료 데이터만 추출
                            if description[i] == '':
                                break
                            if description[i].startswith('['):
                                break
                            if description[i].startswith('[ 만드는 법 ]'):
                                break
                            if description[i].startswith('[만드는 법]'):
                                break
                            if description[i].startswith('*'):
                                break
                            if description[i] == '*':
                                break
                            
                            #! 위에서 재료 데이터를 1차 필터링을 했다면, 재료 데이터에 불필요한 재료 데이터가 들어가 있다면 2차 필터링
                            ingredient = re.sub(r'[|[a-zA-Z]|[0-9]|[약컵큰술개병스푼선택재료각종봉뚜껑있는팩/()+½¼¾~ .-]|]', '', description[i])
                            if '없으면' in ingredient:
                                ingredient = re.sub(r'없으면', '', ingredient)
                            if '생략가능' in ingredient:
                                ingredient = re.sub(r'생략가능', '', ingredient)
                            if '사이즈는일반이입니다' in ingredient:
                                ingredient = re.sub(r'사이즈는일반이입니다', '', ingredient)
                            if '포기' in ingredient:
                                ingredient = re.sub(r'포기', '', ingredient)
                            if '용기' in ingredient:
                                ingredient = re.sub(r'용기', '', ingredient)
                            if '공기' in ingredient:
                                ingredient = re.sub(r'공기', '', ingredient)
                            if '갈아만든배음' in ingredient:
                                ingredient = re.sub(r'갈아만든배음', '', ingredient)
                            if '한줌' in ingredient:
                                ingredient = re.sub(r'한줌', '', ingredient)
                            if '-액젓아무거나' in ingredient:
                                ingredient = re.sub(r'-액젓아무거나', '', ingredient)
                            if '혹은' in ingredient:
                                ingredient = re.sub(r'혹은', '', ingredient)
                            if '전자레인지용기' in ingredient:
                                ingredient = re.sub(r'전자레인지용기', '', ingredient)

                            if (len(ingredient) > 2 and ingredient[-1] == '과') or (len(ingredient) > 2 and ingredient[-1] == '대') or (len(ingredient) > 3 and ingredient[-1] == '간'):
                                ingredient = re.sub(r'.$', '', ingredient)
                            if (len(ingredient) > 3 and ingredient[-1] == '장') or (len(ingredient) > 3 and ingredient[-1] == '와'):
                                ingredient = re.sub(r'(장|와)$', '', ingredient)

                            #! '자취요리신'의 경우엔 재료 정보가 줄 바꿈 없이 문자열 "두부, 순두부, 김치" 이런식으로 되어 있기 때문에 list 형태로 변경하고 for문으로 재료 데이터 추출
                            if channel_name == '자취요리신':
                                ingredient = ingredient.split(',')
                                for i in ingredient:
                                    ingredient_dict = dict(url_pk=url_pk, name=i)
                                    ingredient_list.append(ingredient_dict)
                            else:
                                ingredient_dict = dict(url_pk=url_pk, name=ingredient)
                                ingredient_list.append(ingredient_dict)
            else:
                pass
        
        #* 1. 검증 된 재료데이터(ingredient_list) 를 가져와서 Ingredient Model 에 저장한다.
        obj_list = [Ingredients(name=info['name'], is_valid=True) for info in ingredient_list]
        try:
            Ingredients.objects.bulk_create(obj_list, ignore_conflicts=True)
        except IntegrityError:
            pass

        #* 2. Ingredient Model 이 저장되었고, 
        #*    Ingredient(obj) 의 값을 기준으로 YouTube Model 매칭되는 값을 m2m 으로 연결한다.
        obj_ingredients = Ingredients.objects.all()
        for obj_i in obj_ingredients:
            obj_y = YouTube.objects.filter(description__contains=obj_i.name)
            obj_i.youtube.set(obj_y)
        

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
                thumbnails=video['snippet']['thumbnails']['high']['url']
                view_count=video['statistics'].get('viewCount',0)
                like_count=video['statistics'].get('likeCount',0)
                published=video['snippet']['publishedAt']
                play_time=video['contentDetails']['duration'].strip('PT, S').replace('M', ':')
                stats_dict=dict(url_pk=url_pk, channel_id=channel_id, title=title, description=description, thumbnails=thumbnails, published=published, play_time=play_time, view_count=view_count, like_count=like_count)
                stats_list.append(stats_dict)
        df=pd.DataFrame(stats_list)
        df.to_csv("/home/ubuntu/code/cancook-backend/csv/백종원_쿠킹로그.csv", index=False)
        # df.to_csv("/Users/cslee/vscode/self-dining-backend/csv/백종원_쿠킹로그.csv", index=False)

        obj_list = [YouTube(**data) for data in stats_list] # YouTube(**data) YouTube Object = ORM
        try:
            YouTube.objects.bulk_create(objs=obj_list)
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
                part='id,snippet,statistics,contentDetails',
                id=','.join(video_ids),
                maxResults=50,
            ).execute()
            # ! 자취요리신
            for video in video_details_res['items']:
                url_pk=video['id']
                channel_id=video['snippet']['channelId'] # 'UCC9pQY_uaBSa0WOpMNJHbEQ'
                title=video['snippet']['title']
                description=video['snippet']['description']
                thumbnails=video['snippet']['thumbnails']['high']['url']
                view_count=video['statistics'].get('viewCount',0)
                like_count=video['statistics'].get('likeCount',0)
                published=video['snippet']['publishedAt']
                play_time=video['contentDetails']['duration'].strip('PT, S').replace('M', ':')
                stats_dict=dict(url_pk=url_pk, channel_id=channel_id, title=title, description=description, thumbnails=thumbnails, published=published, play_time=play_time, view_count=view_count, like_count=like_count)
                stats_list.append(stats_dict)
            
            next_page_token = res.get('nextPageToken')
            
            if next_page_token is None:
                break

        df=pd.DataFrame(stats_list)
        df.to_csv("/home/ubuntu/code/cancook-backend/csv/자취요리신.csv", index=False)
        # df.to_csv("/Users/cslee/vscode/self-dining-backend/csv/자취요리신.csv", index=False)

        obj_list = [YouTube(**data) for data in stats_list] # YouTube(**data) YouTube Object = ORM
        try:
            YouTube.objects.bulk_create(objs=obj_list)
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
    elif args.channel == '백종원_재료':
        y.ingredients(channel_name='백종원')
    elif args.channel == '자취요리신_재료':
        y.ingredients(channel_name='자취요리신')
