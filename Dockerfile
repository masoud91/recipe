FROM python:3.7-alpine
MAINTAINER Masoud Aghaei

# turn the output bufffering off on container which is the best practice for pyyhon inside docker
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# apk is alpine's package manager
# --update updates apk repos
# --no-cache prevent from storing apk updates on container to keep it minimal
RUN apk add --update --no-cache postgresql-client

# --virtual following by a temp directory name install packages inside the temp dir
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev

RUN pip install -r /requirements.txt

# delete temporary packages for compiling postgres driver
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user