FROM debian:stable-20220801
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip libreoffice


COPY main.py /home/app/
COPY config /home/app/config/
COPY requirements.txt /home/app/
WORKDIR /home/app/
RUN pip3 install -r requirements.txt
ENTRYPOINT python3 main.py