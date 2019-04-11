FROM alpine:latest

EXPOSE 8081

RUN apk update && apk upgrade

RUN apk add --no-cache --update \
        supervisor \
        uwsgi-python3 \
        python3 \
        nginx \
        git \
        curl \
        tzdata
RUN rm -rfv /var/cache/apk/*

ENV TZ=Europe/Paris
RUN date +"%Y-%m-%dT%H:%M:%S %Z"

COPY . /app

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -v /etc/nginx/conf.d/default.conf


RUN mkdir -p /var/run/nginx && \
    chmod -R 777 /var/run/nginx
RUN mkdir -p /var/run/supervisord /var/log/supervisord && \
    chmod -R 777 /var/run/supervisord
RUN chmod -R 775 /app && \
    chmod -R 777 /usr/sbin && \
    chmod -R 775 /usr/lib/python*
RUN chmod -R 775 /var/lib/nginx && \
    chmod -R 777 /var/log/* && \
    chmod -R 777 /var/tmp/nginx

WORKDIR /app

RUN pip3 install --no-cache-dir -r requirements.txt

# delete all __pycache__-folders in tests-folder
RUN find tests -type d -name __pycache__ -prune -exec rm -rf -vf {} \;
# runs unit tests with @pytest.mark.unit annotation only
RUN python3 -m pytest -svv -m unit tests/

USER 10000
CMD ["/usr/bin/supervisord", "-n"]
