FROM alpine:3.7

EXPOSE 8081
COPY . /app 

RUN apk add --no-cache \
        supervisor \
        uwsgi-python3 \
        python3 \
        nginx \
        git

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

RUN chmod -R 777 /var/lib/nginx && \
    chmod -R 777 /var/log/* && \
    chmod -R 777 /var/tmp/nginx && \
    mkdir -p /var/run/nginx && \
    chmod -R 777 /var/run/nginx && \
    chmod -R 777 /app


WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

USER 10000
CMD ["/usr/bin/supervisord", "-n"]
