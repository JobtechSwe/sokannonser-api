FROM alpine:3.10

EXPOSE 8081

RUN date && apk update && apk upgrade && \
    apk add --no-cache --update \
        uwsgi-python3 \
        python3-dev \
        nginx \
        git \
        curl \
        memcached \
        build-base  \
        tzdata && \
     rm -rfv /var/cache/apk/*

ARG flask_app=sokannonser
ENV flask_app=$flask_app \
    TZ=Europe/Stockholm \
    proc_nr=8

COPY . /app

# COPY nginx.conf /etc/nginx/nginx.conf

RUN date && \
    mkdir -p /var/run/nginx && \
    chmod -R 777 /var/run/nginx && \
    mkdir -p /var/run/supervisord /var/log/supervisord && \
    chmod -R 777 /var/run/supervisord && \
    chmod -R 775 /app && \
    chmod -R 777 /usr/sbin && \
    chmod -R 775 /usr/lib/python* && \
    chmod -R 777 /var/lib/nginx && \
    chmod -R 777 /var/log/* && \
    mkdir -p /var/tmp && \
    chmod -R 777 /var/tmp/


WORKDIR /app

RUN python3 -m pip install --upgrade setuptools wheel pip
RUN python3 -m pip install supervisor
# RUN pip3 install --no-cache-dir -r requirements.txt
# delete all __pycache__-folders in tests-folder
# runs unit tests with @pytest.mark.unit annotation only

RUN echo "" && echo Application: $flask_app && echo Process total: $proc_nr && \
    time pip3 install -r requirements.txt && \
    find tests -type d -name __pycache__ -prune -exec rm -rf -vf {} \; && \
    python3 -m pytest -svv -m unit tests/unit_tests && \
    find tests -type d -name __pycache__ -prune -exec rm -rf -vf {} \;


USER 10000
CMD ["/usr/bin/supervisord", "-n", "-c", "/app/supervisord.conf"]
