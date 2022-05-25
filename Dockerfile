FROM ubuntu:20.04


RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR /app

RUN apt -qq update

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata


RUN apt -qq install -y  python3 python3-pip ffmpeg
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3","-m","bot"]
