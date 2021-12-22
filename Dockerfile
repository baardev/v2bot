FROM python:latest

WORKDIR /v2bot

ENV PORT 80
ENV PYTHONUNBUFFERED 1

#COPY . /v2bot
#RUN #cat /etc/os-release

RUN apt-get update
RUN apt-get install -y joe
RUN apt-get install -y apt-utils
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get install -y git
RUN apt-get install -y wget
RUN apt-get install -y x11vnc xvfb
RUN apt-get install -y qtcreator
RUN apt-get install -y gnumeric
RUN apt-get install -y unzip
RUN apt-get install -y mariadb-server
RUN apt-get install -y mariadb-client

RUN #wget  http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
RUN #tar zxvf ta-lib-0.4.0-src.tar.gz
RUN #ta-lib/configure
RUN #pip install TA-Lib

RUN pip install -r /v2bot/requirements.txt
RUN git clone git@github.com:baardev/v2bot.git /v2bot
RUN cd v2bot
RUN wget -O data.zip  https://mega.nz/file/F2x0WIqS\#AcJZvEACTIYqo92PnKaCpjdpHm8hGk2H29dzUbtFl0g
RUN unzip data.zip
RUN cd /