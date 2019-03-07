FROM ubuntu:latest
RUN apt-get update
    && apt-get install python3 python3-pip
WORKDIR /code
COPY . /code
RUN python3 -m pip install virtualenv
RUN python3 -m virtualenv venv
RUN source venv/bin/activate
RUN pip install -r requirements.txt
RUN python pyinstaller.py
VOLUME /code
