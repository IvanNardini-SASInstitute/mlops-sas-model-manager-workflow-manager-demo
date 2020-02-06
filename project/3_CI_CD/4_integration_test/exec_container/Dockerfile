FROM alpine:latest

RUN apk add --no-cache --update curl

WORKDIR /home/test

EXPOSE 9998

COPY ./test.csv /home/test
