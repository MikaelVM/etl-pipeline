# Test
FROM python:3.14-slim

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN pip3 install --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY ./src /app/
RUN mkdir /data

CMD ["python3", "main.py"]
# CMD ["uvicorn", "./api/api:app", "--host", "0.0.0.0", "--port", "80"]

