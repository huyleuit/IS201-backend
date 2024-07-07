
FROM python:3.10-alpine3.19
WORKDIR /app
RUN apk update && \
    apk upgrade && \
    apk add --no-cache build-base && \
    apk add curl
COPY ./app/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./app .
RUN adduser -h /app -D is210 && \
    chown -R is210:is210 /app && \
    chmod -R 700 /app && \
    rm -rf /var/cache/apk/* \
    apk del build-base
CMD ["python","main.py"]
EXPOSE 8009
