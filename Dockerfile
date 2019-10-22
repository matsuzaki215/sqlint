FROM python:3.7.4

ENV LC_ALL C.UTF-8
ENV LANG   C.UTF-8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl gcc g++ bash python3 python3-pip python3-dev && \
    apt-get install -y --no-install-recommends sudo unzip vim && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY src /work
COPY tox.ini /work
COPY tests /work/tests
WORKDIR /work
