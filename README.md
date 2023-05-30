# self-dining-backend

## feat
1. Django Model 생성 완료
2. AWS EC2, RDS 생성 완료
3. YouTube Data 백종원, 자취요리신 데이터 RDS 저장 완료
4. Pandas to_csv 로 csv 파일 생성 완료
5. 가비아 도메인 구매 완료 self-dining.shop
6. sshtunnel <br> settings.py
   ```
   from sshtunnel import SSHTunnelForwarder
   # # SSH
   # ! AWS EC2 에서는 주석처리
   server = SSHTunnelForwarder(
      (os.getenv('AWS_EC2_IP'), 22),
      ssh_username=os.getenv('AWS_EC2_USERNAME'),
      ssh_pkey='~/.ssh/8th-team2.pem',
      remote_bind_address=(
         os.getenv('POSTGRES_HOST'), 5432
      )
   )
   server.stop()
   server.start()

   DATABASES = {
      'default': {
         'ENGINE': 'django.db.backends.postgresql',
         # ! 로컬 환경에서는 아래와 같이 설정
         'HOST': '127.0.0.1',
         # ! AWS EC2 에서는 아래와 같이 설정
         # 'HOST': os.getenv('POSTGRES_HOST'),
         'NAME': os.getenv('POSTGRES_NAME'),
         'USER': os.getenv('POSTGRES_USER'),
         'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
         # ! 로컬 환경에서는 아래와 같이 설정
         'PORT': server.local_bind_port,
         # ! AWS EC2 에서는 아래와 같이 설정
         # 'PORT': 5432,
      }
   }
   ```
   youtube.py
   ```
   with SSHTunnelForwarder(
        (os.getenv('AWS_EC2_IP'), 22),
        ssh_username=os.getenv('AWS_EC2_USERNAME'),
        ssh_pkey='~/.ssh/8th-team2.pem',
        remote_bind_address=(
            os.getenv('POSTGRES_HOST'), 5432
        )
    ) as tunnel:
        if tunnel.is_active:
            print("AWS EC2 SSH 터널이 성공적으로 연결되었습니다.")
        else:
            print("AWS EC2 SSH 터널 연결에 실패하였습니다.")

        postgres_password = os.getenv('POSTGRES_PASSWORD')
        postgres_port = tunnel.local_bind_port # * 외부에서는 5432, 내부에서는 랜덤으로 할당되는 포트번호
   ```

## TODO
1. AWS EC2
   1. 내부에서 Docker 사용
   2. Nginx 설정 Frontend, Backend
   3. SSL 인증서 발급 HTTPS 적용
2. YouTube Data 백종원, 자취요리신 데이터 리펙터링
3. Django config/settings/ local.py, dev.py 설정파일 생성