FROM        python:3.8-slim

RUN         apt-get -y -qq update && \
            apt-get -y -qq dist-upgrade && \
            apt-get -y -qq autoremove

RUN         apt -y install nginx

COPY        ./requirements.txt /tmp/
RUN         pip install -r /tmp/requirements.txt

COPY        . /srv/dev_log/backend/
WORKDIR     /srv/dev_log/backend/app


RUN         rm /etc/nginx/sites-available/default
RUN         rm /etc/nginx/sites-enabled/default
RUN         cp /srv/dev_log/backend/.config/app.nginx /etc/nginx/sites-available/
RUN         ln -s /etc/nginx/sites-available/app.nginx /etc/nginx/sites-enabled/app.nginx
RUN         mkdir /var/log/gunicorn

CMD         /bin/bash