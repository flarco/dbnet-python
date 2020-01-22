FROM continuumio/anaconda3:2019.10

RUN apt-get update && \
  apt-get install -y software-properties-common gcc cmake && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists /var/cache/apt

ADD . /app

RUN pip install -e /app

EXPOSE 5566

WORKDIR /app

ENTRYPOINT [ "dbnet" ]