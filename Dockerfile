FROM ubuntu:latest
RUN apt-get update && \
    apt-get -y install python3 python3-pip
RUN python3 -m pip install --upgrade pip
WORKDIR /code
COPY . /code
RUN python3 -m pip install -r requirements.txt && \
    export UPX_PATH=/usr/local/bin/upx && \
    python3 pyinstaller.py
CMD ["python"]
