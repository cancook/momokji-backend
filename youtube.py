import os, re
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
from search.models import Ingredients


class YouTubes():
    def __init__(self):
        DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
        YOUTUBE_API_SERVICE_NAME='youtube'
        YOUTUBE_API_VERSION='v3'
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    def paik_jong_won_ingredients(self):
        ingredient_dict = {}
        ingredient_list = []
        target_description = None

        objs = YouTube.objects.filter(channel_id="UCyn-K7rZLXjGl7VXGweIlcA").values_list('url_pk', 'description')
        """
        1. 유튜브 재료 데이터 저장 Model 을 만든다.
            - YouTube <-> YouTube Ingredient
            - YouTube(id) video OneToMany YouTube Ingredient 재료데이터
        2. YouTube description 데이터에서 유튜브 재료 데이터 저장 Model 에 저장이 되어있는지 여부 확인
            - 저장 되어 있다면 pass
            - 저장 안되어 있다면 저장 bulk_create
        3. 나무위키 데이터를 사용하지 않고, 유튜브 데이터를 계속 쌓아가는 방식으로 사용
        """
        for obj in objs:
            description = obj[1].split("\n")
            url_pk = obj[0]
            for ingredient in description:
                if '[ 재료 ]' in ingredient:
                    target_description = ingredient
                    if target_description:
                        index = description.index(target_description)
                        for i in range(index+1, len(description)):
                            if description[i] == '':
                                break
                            if description[i].startswith('['):
                                break
                            if description[i].startswith('[ 만드는 법 ]'):
                                break
                            if description[i].startswith('*'):
                                break
                            if description[i] == '*':
                                break

                            ingredient = re.sub(r'[|[a-zA-Z]|[0-9]|[약컵큰술개병/()½¼¾~ .]|]', '', description[i])
                            if (len(ingredient) > 2 and ingredient[-1] == '과') or (len(ingredient) > 2 and ingredient[-1] == '대') or (len(ingredient) > 3 and ingredient[-1] == '간'):
                                ingredient = re.sub(r'.$', '', ingredient)
                            if (len(ingredient) > 3 and ingredient[-1] == '장') or (len(ingredient) > 3 and ingredient[-1] == '와'):
                                ingredient = re.sub(r'(장|와)$', '', ingredient)

                            ingredient_dict = dict(url_pk=url_pk, name=ingredient)
                            ingredient_list.append(ingredient_dict)
            else:
                pass
        
        obj_list = [Ingredients(name=info['name'], is_valid=True) for info in ingredient_list]
        for obj in obj_list:
            try:
                obj.save()
            except IntegrityError:
                pass

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
                thumbnails=video['snippet']['thumbnails']['high']
                view_count=video['statistics'].get('viewCount',0)
                like_count=video['statistics'].get('likeCount',0)
                published=video['snippet']['publishedAt']
                play_time=video['contentDetails']['duration'].strip('PT, S').replace('M', ':')
                stats_dict=dict(url_pk=url_pk, channel_id=channel_id, title=title, description=description, thumbnails=thumbnails, published=published, play_time=play_time, view_count=view_count, like_count=like_count)
                stats_list.append(stats_dict)
        df=pd.DataFrame(stats_list)
        df.to_csv("/home/ubuntu/code/cancook-backend/csv/백종원_쿠킹로그.csv", index=False)

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
                thumbnails=video['snippet']['thumbnails']['high']
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


class IngredientList():
    def namuwiki(self):
        ingredients = ['곡물', '쌀', '밀', '옥수수', '콩', '강낭콩', '대두', '렌틸', '병아리콩', '서리태', '완두', '풋콩', '녹두', '팥', '보리', '엿기름', '청보리', '귀리', '오트밀', '기장(식물)|기장', '수수', '율무', '조(식물)|조', '카무트', '피(식물)|피', '참깨', '호밀', '메밀', '아마란스', '견과류', '갈릭넛', '개암나무', '도토리', '땅콩', '마카다미아', '밤(열매)|밤', '브라질너트', '아마씨', '아몬드', '은행나무|은행', '잣', '캐슈넛', '피스타치오', '피칸', '해바라기씨', '헤이즐넛', '호두', '호박씨', '과일', '귤속', '딸기', '산딸기', '블랙베리', '라즈베리', '블루베리', '크랜베리', '넌출월귤', '배(과일)|배', '서양배', '키위(과일)|키위', '다래', '파인애플', '포도', '건포도', '복숭아', '천도복숭아', '감|감', '구아바', '구즈베리', '꽃사과', '대추', '대추야자', '두리안', '람부탄', '리치(과일)', '망고', '망고스틴', '매실', '머루', '멜론', '모과', '무화과', '바나나', '버찌', '앵두', '체리', '보리수', '복분자', '빵나무', '사과', '살구', '수박', '스타후르츠', '시솝', '애플망고', '옐로베리', '용과', '용안', '이리사바이', '자두', '잭프루트', '진들딸기', '참외', '코코넛', '파파야', '채소', '감자', '고구마', '고사리', '근대(채소)|근대', '당근', '돌나물', '돈나물', '무(채소)|무', '배추', '브로콜리', '상추', '아스파라거스', '양배추', '오이', '콩나물', '숙주나물', '케일', '토마토', '호박', '우엉', '연근', '마(식물)|마', '야콘', '가지(채소)|가지', '피망', '파프리카', '양파', '시금치', '부추', '미나리', '쑥갓', '고기|육류', '쇠고기', '돼지고기', '닭고기', '양고기', '오리고기', '칠면조', '비둘기', '말고기', '염소고기', '고래고기', '쥐고기', '개고기', '배양육', '가공육', '유제품', '우유', '원유', '가공우유', '치즈', '버터', '요구르트', '야쿠르트', '연유', '분유', '생크림', '휘핑크림', '사워크림', '생선', '생선|문서', '꼴뚜기', '낙지', '문어', '오징어', '쭈꾸미', '해삼', '게', '꽃게', '대게', '참게', '새우', '대하', '바닷가재', '닭새우', '조개|패각류', '꼬막', '굴(어패류)|굴', '대합', '모시조개', '바지락', '소라(동물)|소라', '전복', '재첩', '키조개', '홍합', '조류(식물)|해조류', '감태', '김(음식)|김', '다시마', '매생이', '모자반', '미역', '톳', '파래', '충식|곤충류', '누에', '번데기(음식)|번데기', '거저리', '메뚜기', '조미료', '장류', '식용유', '스프레드(식품)|스프레드', '당|당류', '설탕', '흑설탕', '사탕수수', '올리고당', '정제당', '삼온당', '황설탕', '조청', '꿀', '땅콩버터', '시럽', '메이플 시럽', '아가베 시럽', '버터스카치', '청(식재료)', '액상과당', '잼(음식)|잼', '마멀레이드', '허니버터', '타가토스', '베지마이트', '마마이트', '양념', '소스', '드레싱', '마요네즈', '랜치', '홀랜다이즈 소스', '머스터드 소스', '케첩', '케찹 마니스', '살사', '우스터 소스', '핫소스', '타바스코', '타르타르 소스', '스리라차 소스', '젓갈', '액젓', '피시소스', '멸치젓소스', '커리', '마살라', '갖은양념', '다대기', '브라운 소스', '그레이비 소스', '데미글라스 소스', '데리야키', '베샤멜 소스', '시즈닝', '참소스', '초고추장', '토마토 소스', '소금', '죽염', '토판염', '암염', '식초', '발사믹 식초', '육수', '스톡', '가쓰오부시', '후리카케', '향신료', '허브(식물)|허브', '고추', '후추', '파', '대파(식물)|대파', '쪽파', '겨자', '머스터드', '생강', '강황', '터메릭', '시나몬', '계피', '고추냉이', '마늘', '바닐라', '사프란', '깻잎', '들깨', '달래', '차조기', '회향', '커민', '소두구', '육두구', '메이스', '타마린드', '올스파이스', '산초(식물)|산초', '팔각', '정향', '귤|진피', '오신채', '색소', '치자나무|치자', '쪽', '캐러멜 색소', '화학조미료', '다시다', '사카린', '아스파탐', '자일리톨', 'MSG', '미원(조미료)|미원', '아지노모토', '수크랄로스', '산화방지제', '삼차뷰틸하이드로퀴논', '스테비오사이드', '팽창제', '베이킹 파우더', '탄산수소나트륨', '가공식품', '보존식품', '통조림', '참치통조림', '고추참치', '병조림', '식물성 고기', '대두단백', '콩고기', '밀고기', '어묵', '게맛살', '핫바', '두부', '유부', '냉동식품', '레토르트 식품', '시리얼', '만두', '참치마요', '에너지바', '두유', '아몬드밀크', '마가린', '미숫가루', '면', '국수', '파스타', '기호식품', '커피', '차', '술', '술 관련 정보', '음료', '주스', '탄산음료', '사이다', '소다', '진저에일', '콜라', '토닉워터', '이온음료', '감주', '량샤', '숙취해소제', '에너지 드링크', '초콜릿', '카카오', '카카오매스', '카카오버터', '카카오 파우더', '카카오닙스', '다크 초콜릿', '화이트 초콜릿', ':분류:초콜릿', '과자', ':분류:과자', '과자/공산품', '한과', '한국', '화과자', '일본', '풀빵', '서양', '누가', '바', '비스킷', '사탕', '스낵', '크래커', '칩', '아이스크림', ':분류:빙과류', '빵', '빵/종류', '건빵', '공갈빵', '꿀빵', '모닝빵', '바게트', '쇼트케이크', '소보로빵', '슈크림빵', '슈크림', '소라빵', '초코 콜로네', '스펀지 케이크', '시폰 케이크', '식빵', '웨딩케이크', '진저브레드', '치즈케이크', '컵케이크', '파운드 케이크', '파이(음식)|파이', '팬케이크', '핫케이크', '케이크', '쿠키', '아이스크림 케이크']
        
        for ingredient in ingredients:
            Ingredients.objects.create(name=ingredient)

if __name__ == '__main__':
    slack_token = os.getenv('SLACK_TOKEN')
    client = WebClient(token=slack_token)

    parser = argparse.ArgumentParser(description='you must choose 백종원 and 자취요리신')
    parser.add_argument('-c', '--channel')
    parser.add_argument('-i', '--ingredients')
    args = parser.parse_args()

    y = YouTubes()
    ingredient = IngredientList()

    if args.channel == '백종원':
        y.paik_jong_won_ingredients()
    elif args.channel == '자취요리신':
        y.simple_cooking()
    elif args.ingredients == '나무위키':
        ingredient.namuwiki()
