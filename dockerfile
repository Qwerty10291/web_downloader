FROM alpine

EXPOSE 8000

RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add py3-numpy py3-pandas git py3-pip g++ 

RUN git clone https://github.com/Qwerty10291/web_downloader \
    && cd web_downloader && pip3 install -r requirements.txt

WORKDIR /web_downloader

ENTRYPOINT python3 app.py