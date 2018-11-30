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
RUN rm -rf /var/cache/apk/*

ENV TZ=Europe/Paris
RUN date +"%Y-%m-%dT%H:%M:%S %Z"

COPY . /app

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

#cd COPY supervisord.conf /etc/supervisord.conf


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
# show commit info
RUN git log -1

# runs unit tests with @pytest.mark.unit annotation only
RUN python3 -m pytest -svv -m unit tests/
RUN rm -rf ./pytest_cache sokannonser/__pycache__
RUN git log -1

USER 10000
CMD ["/usr/bin/supervisord", "-n"]
#CMD ["/usr/bin/supervisord", "-n" "-c", "/app/supervisord.conf"]
