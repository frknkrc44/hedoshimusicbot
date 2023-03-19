FROM nikolaik/python-nodejs:python3.11-nodejs18-alpine
RUN apk update \
    && apk upgrade \
    && apk add ffmpeg git gcc musl-dev linux-headers

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -U pip -r requirements.txt
CMD ["python3", "-m", "hedoshi"]
