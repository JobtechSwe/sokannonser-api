FROM alpine:latest

EXPOSE 8081

RUN apk update && apk upgrade

RUN apk add --no-cache --update \
        supervisor \
        uwsgi-python3 \
        python3 \
        nginx \
        git \
        curl

COPY . /app

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

RUN chmod -R 775 /var/lib/nginx && \
    chmod -R 777 /var/log/* && \
    chmod -R 777 /var/tmp/nginx
RUN mkdir -p /var/run/nginx && \
    chmod -R 777 /var/run/nginx
RUN chmod -R 775 /app && \
    chmod -R 777 /usr/sbin && \
    chmod -R 775 /usr/lib/python*

WORKDIR /app

RUN pip3 install --no-cache-dir -r requirements.txt
# runs unit tests with @pytest.mark.unit annotation only
RUN python3 -m pytest -svv -m unit tests/
# show commit info
RUN git log -1

USER 10000
CMD ["/usr/bin/supervisord", "-n"]
