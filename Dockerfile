FROM python:3.14-slim

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN pip3 install --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY ./docker-test.py /app/docker-test.py

CMD ["python3", "docker-test.py"]
