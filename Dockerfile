FROM python:3.7

ADD . /app

RUN pip install -e /app

EXPOSE 5566

WORKDIR /app

ENTRYPOINT [ "dbnet" ]