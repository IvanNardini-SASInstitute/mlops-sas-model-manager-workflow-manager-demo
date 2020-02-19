FROM python:3

LABEL maintainer="Ivan Nardini <ivan.nardini@sas.com>"
LABEL description="A basic python:3 image modified for data quality test "

ENV PYLINTHOME=.

WORKDIR /usr/src/app

RUN pip install pylint numpy pandas joblib sklearn
RUN pip install xgboost
RUN pip3 install pymongo