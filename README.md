# dev_log

## 이슈 기록
 
### AWS ubuntu 초기 설정

- 2020 2월 기준 ubuntu 최신 (20.04) 버전에서 도커 설치에 문제가 있어서 18.04 버전에서 진행

```bash
sudo apt update

# 설치된 패키지 의존성 검사 및 업그레이드
sudo apt dist-upgrade

sudo apt install zsh

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

sudo chsh ubuntu -s /usr/bin/zsh

# docker
sudo apt update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# ubuntu 18.04 기준
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"

sudo apt install docker-ce

# docker sudo 없이 명령어 사용하기
# 사용자를 docker 그룹에 등록
sudo usermod -aG docker ubuntu(현재 사용자)
#설정 후 재기동
sudo systemctl reboot
# 재기동 없이 사용하려면
sudo -su -ubuntu(현재사용자)

# 다음 에러 발생시
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/json: dial unix /var/run/docker.sock: connect: permission denied

sudo chmod 666 /var/run/docker.sock

# docker-compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 실행 권한
sudo chmod +x /usr/local/bin/docker-compose
```
---

## Nginx, gunicorn, supervisor 설정

- app.nginx

```bash
server {
    listen                  80;
		# server_name 서브 도메인까지 설정(' '스페이스로 구분)
    server_name             hswlog.dev www.hswlog.dev;
    charset                 utf-8;
		
		# http (80번포트)로 오면 모조리 https(443번포트)로 리다이렉트
    location / {
        return              301 https://$host$request_uri;
}

server {
    listen                  443 ssl;
    server_name             hswlog.dev www.hswlog.dev;
    charset                 utf-8;
		
		# letsencrypt로 공짜로 https 암호화 가능
		# 아래는 ssl 사용여부 및 암호화 파일 위치 설정
    ssl                     on;
    ssl_certificate         /etc/letsencrypt/live/hswlog.dev/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/hswlog.dev/privkey.pem;
		
		# https(443번포트)로 요청이 왔을때
    location / {
        include             /etc/nginx/proxy_params;
				# 8000번 포트가 아닌 unix 소켓을 사용
				# 리눅스계열에서는 unix 소켓이 안정적이고 성능이 좋다고 합니다
        proxy_pass          http://unix:/run/dev_log.sock;
    }
		
		# 정적 파일들을 찾으면 어디로 보낼 것인가
		# 이 프로젝트의 경우 AWS S3 사용중이므로 S3 버킷 주소를 설정
    location /static/ {
        alias               http://버킷이름.AWS리전이름.amazonaws.com;
    }

}
```

- gunicorn.py

```python
daemon = False
# manage.py dir
chdir = '/srv/dev_log/backend/app'

# bind 부분의 소켓 이름을 nginx 설정과 맞춰야 함
bind = 'unix:/run/dev_log.sock'

accesslog = '/var/log/gunicorn/dev_log-access.log'
errorlog = '/var/log/gunicorn/dev_log-error.log'
capture_output = True
```

- supervisor.conf

```bash
# supervisord : 프로세스 관리 (nginx 죽으면 재시작 해준다던가.. 등등)

[supervisord]
logfile = /var/log/supervisord.log
# 프로세스 사용자 이름 (ex: root)
user = root

[program:nginx]
command = nginx -g 'daemon off;'

# gunicorn을 -b 0.0.0.0;8000 .. 포트로 실행하지 않고 gunicorn.py의 설정된 값으로 실행
[program:gunicorn]
command = gunicorn -c /srv/dev_log/backend/.config/gunicorn.py config.wsgi.production
```
---

## 장고 서버 배포 (스크립트 흐름)

로컬에서 docker run

1. build
- poetry export
- docker build

2. copy secret(env)

- docker run (bash)
- docker cp secret(env)

3. run

- collectstatic
- docker run(supervisor)

배포부터 run까지

1. (로컬) build, push
2. (서버) pull, run(bash)
3. (로컬) secret(env)를 서버로 copy
4. (서버) secret(env)를 container로 copy
5. (서버) run
- collectstatic
- docker run (supervisor)

- 위의 스크립트 흐름을 작성 (작성된 도커파일 → docker hub에 이미지 업로드→ AWS ec2 접속 → docker image 다운로드 및 컨테이너 키고 nginx, gunicorn (80번, 443번 포트) 띄우는 상태 까지 자동
- deploy.py

```python
#!/usr/bin/env  python3.8

import os
import subprocess
from pathlib import Path

# decouple: config() <- .env 파일을 상위 디렉토리까지 쭉 찾아서 환경변수 가져옵니다
from decouple import config

IDENTITY_FILE = os.path.join(str(Path.home()), '.secret_path', 'xxxx.pem')
USER = config('USER')
HOST = config('HOST')
TARGET = f'{USER}@{HOST}'
DOCKER_IMAGE_TAG = config('DOCKER_IMAGE_TAG')
PROJECT_NAME = config('PROJECT_NAME')
ENV_FILE = os.path.join(os.path.join(str(Path.home()), config('PROJECT_DIR'), 'sub_dir'), '.env')

DOCKER_OPTIONS = (
    ('--rm', ''),
    ('-it', ''),
    ('-d', ''),
    ('-p', '80:80'),
    ('-p', '443:443'),
    ('-v', '"/etc/letsencrypt:/etc/letsencrypt"'),
    ('--name', f'{PROJECT_NAME}'),
)

def run(cmd, ignore_error=False):
    process = subprocess.run(cmd, shell=True)

    if not ignore_error:
        process.check_returncode()

def ssh_run(cmd, ignore_error=False):
    run(f'ssh -o StrictHostKeyChecking=no -i {IDENTITY_FILE} {TARGET} {cmd}', ignore_error=ignore_error)

def local_build_push():
    run(f'poetry export -f requirements.txt > requirements.txt')
    run(f'docker system prune -f')
    run(f'docker build -t {DOCKER_IMAGE_TAG} .')
    run(f'docker push {DOCKER_IMAGE_TAG}')

def server_init():
    ssh_run(f'sudo apt -y update')
    ssh_run(f'sudo apt -y dist-upgrade')
    ssh_run(f'sudo apt -y autoremove')
    ssh_run(f'sudo apt -y install docker.ce')

def server_pull_run():
    ssh_run(f'sudo docker pull {DOCKER_IMAGE_TAG}')
    ssh_run(f'sudo docker stop {PROJECT_NAME}', ignore_error=True)
    ssh_run(f'sudo docker system prune -f')
    ssh_run('sudo docker run {options} {tag}'.format(
        options=' '.join([f'{key} {value}' for key, value in DOCKER_OPTIONS]),
        tag=DOCKER_IMAGE_TAG
    ))

# env 비밀값들 ec2에 복사 -> (docker run 후) docker에 복사
def copy_secrets():
    run(f'scp -i {IDENTITY_FILE} {ENV_FILE} {TARGET}:/tmp')
    ssh_run(f'sudo docker cp /tmp/.env {PROJECT_NAME}:/srv/{PROJECT_NAME}/sub_dir')

def server_exec():
    ssh_run(
        f'sudo docker exec {PROJECT_NAME} python manage.py collectstatic --settings config.settings.production --noinput')
    ssh_run(f'sudo docker exec -d {PROJECT_NAME} supervisord -c /srv/{PROJECT_NAME}/sub_dir/.config/supervisord.conf')

if __name__ == '__main__':
    try:
        print('--- DEPLOY START! ---')
        local_build_push()
        print('---> LOCAL BUILD AND PUSH COMPLETED.')
        server_init()
        print('---> SERVER INITIAL SETTINGS COMPLETED.')
        server_pull_run()
        print('---> SERVER PULL AND RUN COMPLETED.')
        copy_secrets()
        print('---> SECRETS COPY COMPLETED.')
        server_exec()
        print('---> SERVER EXECUTE COMPLETED.')
        print('--- DEPLOY SUCCESS! ---')

    except subprocess.CalledProcessError as e:
        print('--- DEPLOY FAILED... ---')
        print('CMD >> ', e.cmd)
        print('RETURNCODE >> ', e.returncode)
        print('OUTPUT >> ', e.output)
        print('STDOUT >> ', e.stdout)
        print('STDERR >> ', e.stderr)
```
---

## Let's Encrypt

- 인증서 발급
- 인증서와 공개키, 개인키를 Nginx가 사용하게 해야 함(443 포트 설정)
- 인증서는 3개월마다 갱신해줘야 함(안 그러면 https 해제)

```bash
# 도커 사용 안할때 ubuntu 명령어로 갱신
sudo snap install core; sudo snap refresh core

# 설치되어 있다면 제거
sudo apt remove certbot 

sudo snap install --classic certbot

sudo ln -s /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx

sudo certbot certonly --nginx

# 실제 실행 전 갱신 테스트
sudo certbot renew --dry-run
```

- 성공했다면 아래 경로에 암호화 파일 생성
- /etc/letsencrypt/live/(도메인이름)/키
- /etc/letsencrypt/live/hswlog.dev/fullchain.pem
- /etc/letsencrypt/live/hswlog.dev/privkey.pem
- Your certificate will expire on 2021-06-10

```bash
# 도커를 사용한다면
# 도커 1회 실행해서 letsencrypt 인증(certbot/certbot)
docker run --rm -it --name certbot -v '/etc/letsencrypt:/etc/letsencrypt' -v '/var/lib/letsencrypt:/var/lib/letsencrypt' \
certbot/certbot certonly -d 'hswlog.dev,www.hswlog.dev' --manual

# --rm 옵션이 붙어서 인증 끝나면 컨테이너는 지워짐
# 위의 인증 방법은 해당 도메인이 자기 사이트인지 입증을 해야 합니다
# app.nginx
# 예시 : 도메인//.well-known/acme-challenge/xxxx...에 접속하면 xxxxxxx가 보여야 한다
location /.well-known/acme-challenge/ {
		alias               /srv/dev_log/.cert/;
}
```
---

## Django Post에  Markdown 적용

- 고려할만한 라이브러리
1. django-summernote
2. django-ckeditor (파일 업로드 부분 유료라는 글을 보았음)
3. 앞의 1, 2는 텍스트 에디터의 확장 기능이고, 어드민에 마크다운 문법만 적용되면 아무거나 괜찮았다
4. (블로그는 나만 글을 작성할 것이고, post 에디트 페이지는 필요 없다 판단했다)
5. mator 도 사용해봤는데.. 설정 착오인지 어드민에서 텍스트 폼 란이 깨졌다

### django-markdownx 사용

- docs : [https://neutronx.github.io/django-markdownx/](https://neutronx.github.io/django-markdownx/)
- 설치

```bash
pip install django-markdownx
pip install Pygments
```

- 장고 settings 설정

```python
INSTALLED_APP =[
    # 생략
    'markdownx',
]

MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.toc',
    'markdown.extensions.codehilite',
    'markdown.extensions.fenced_code',
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
    'markdown.extensions.codehilite': {
        'linenums': True,
        'use_pygments': True,
        'noclasses': True
    }
}
```

- extra는 마크다운 각주, 테이블 등 확장된 기능을 제공
- fenced_code는 코드 블락을 지원
- codehilite는 코드와 문법 하이라이팅을 지원
- 기타 다른 설정([https://python-markdown.github.io/extensions/code_hilite/](https://python-markdown.github.io/extensions/code_hilite/))
- 모델 텍스트 필드를 마크다운 필드로 수정

```python
class Post(models.Model):
    # 생략
    # content = models.TextField()
    content = MarkdownxField()

		# 추가
    def formatted_markdown(self):
        return markdownify(self.content)
```

- [admin.py](http://admin.py) → MarkdownxModelAdmin 상속

```python
# 생략
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = ('id', 'author', 'title', 'content' ...)

```

- [urls.py](http://urls.py) 에 추가

```python
from django.urls import path, include

urlpatterns = [
    # 생략
    path('markdownx/', include('markdownx.urls')),
]
```

- 마크다운 적용을 위한 정적 파일 모으기

```bash
python manage.py collectstatic
```


## Frontend

### Vue와 django 연결

- django

```bash
pip install django-webpack-loader
```

```python
INSTALLED_APPS = (
    ...
    'webpack_loader',
)

# WebPack Loader
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(PROJECT_DIR, 'frontend', 'webpack-stats.json'),
    }
}
```

```python
# Template에 적용할 때 예시
{% load render_bundle from webpack_loader %}

{% render_bundle 'app' %}
```

- 위 설정을 보면 webpack-stats.json이라는 파일에서 파일을 참고하는데, 그 파일은 프론트엔드에서 별도로 설치해야 함

- Vue.js 외에 추가로 설치 (장고에서 화면을 보기 위함)

```bash
# 주의사항 : 현재기준(2021.03) 최신 버전(1.0.0 alpha)은 오류가 있어서 0.4.3 버전을 설치해야 함 
npm install --save-dev webpack-bundle-tracker@0.4.3
```

- 웹팩 설정 예시

```jsx
// vue.config.js

const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  publicPath: "http://0.0.0.0:8080/",
  outputDir: './dist/',

  chainWebpack: config => {

    config
        .plugin('BundleTracker')
        .use(BundleTracker, [{filename: './webpack-stats.json'}])

    config.output
        .filename('bundle.js')

    config.optimization
        .splitChunks(false)

    config.resolve.alias
        .set('__STATIC__', 'static')

    config.devServer
        .public('http://127.0.0.1:8080')
        .host('127.0.0.1')
        .port(8080)
        .hotOnly(true)
        .watchOptions({poll: 1000})
        .https(false)
        .disableHostCheck(true)
        .headers({"Access-Control-Allow-Origin": ["\*"]})

  },

  // 아래 주석 코드는 배포작업(npm run build) 하기 전 해제한다
  // css: {
  //     extract: {
  //       filename: 'bundle.css',
  //       chunkFilename: 'bundle.css',
  //     },
  // }

};
```

- 설정 후 프론트 띄우기

```bash
npm run serve
```

- 이후에  webpack-stats.json 가 생성된 것을 확인
- 장고에서 스태틱 디렉토리 추가 설정 예시

```python
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_FRONTEND_ASSETS_DIR = os.path.join(PROJECT_DIR, 'frontend/assets')
STATIC_FRONTEND_DIST_DIR = os.path.join(PROJECT_DIR, 'frontend/dist')
STATIC_ROOT = os.path.join(ROOT_DIR, 'static')
STATICFILES_DIRS = [
    STATIC_DIR,
    STATIC_FRONTEND_ASSETS_DIR,
    STATIC_FRONTEND_DIST_DIR,
]
```

- 화면 테스트를 위한 코드 (홈 화면에 표시)

```python
# views.py
from django.conf import settings
from django.views.generic import TemplateView

class IndexTemplateView(TemplateView):

    def get_template_names(self):
				# dev 설정, production 설정 구분
        if settings.DEBUG:
            template_name = "index-dev.html"
        else:
            template_name = "index.html"
        return template_name

# urls.py
urlpatterns = [
		...
    path('', IndexTemplateView.as_view(), name='home')
]
```
```html
<!-- Templates 예시-->
# base.html
<!doctype html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Balsamiq+Sans">

    {% block style %}
    {% endblock %}
</head>
<body>
        {% block content %}
        {% endblock %}

        {% block js %}
        {% endblock %}
</body>
</html>


<!--index-dev.html (dev mode)-->

{% extends 'base.html' %}
{% load render_bundle from webpack_loader %}

{% block content %}
<noscript>
    <strong>We're sorry but frontend doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
</noscript>
<div id="app"></div>

<!-- built files will be auto injected -->
{% render_bundle 'app' %}
{% endblock %}


<!--index.html (production mode)-->

{% extends "base.html" %}
{% load static %}

{% block style %}
    <link type="text/css" href="{% static 'bundle.css' %}">
{% endblock %}

{% block content %}
<noscript>
    <strong>We're sorry but frontend doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
</noscript>
<div id="app"></div>
{% endblock %}

{% block js %}
    <script type="text/javascript" src="{% static 'bundle.js' %}"></script>
{% endblock %}
```

- vue, django 모두 run 후 확인

```bash
# frontend
npm run serve

# backend
python manage.py runserver

# django runserver 화면에서 frontend 잘 보이는지 확인
```