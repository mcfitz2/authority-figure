FROM python:3-alpine

RUN apk add --no-cache git
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "./loader.py" ]
