# Environment
FROM ubuntu:latest
COPY . /tmp/Proyecto
WORKDIR /tmp/Proyecto/App/cir_parser_app
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y ngspice
RUN apt-get install -y libngspice0-dev
RUN apt-get install -y x11-xserver-utils
RUN apt-get install -y python3-pip
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Costa_Rica
RUN apt-get install -y python3-tk
RUN pip3 install -r ./../requirements.txt
CMD [ "python3", "./src/ui.py" ]
#CMD [ "python3", "./src/main.py" ]
