FROM python:3.11-slim

RUN python3 -m pip install --upgrade pip \
  && python3 -m pip install wheel

WORKDIR /code
# ADD requirements.txt .
# RUN python3 -m pip install --no-cache-dir -r requirements.txt

ADD . .
RUN python3 -m pip install -e .
