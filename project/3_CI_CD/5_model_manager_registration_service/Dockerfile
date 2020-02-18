FROM python:3

LABEL maintainer="Ivan Nardini <ivan.nardini@sas.com>"
LABEL description="A basic python:3 image modified for SAS Model Registring Service "

USER root

RUN pip install --upgrade pip; \
    pip install requests; \
    pip install sendgrid;

WORKDIR /pyservice/registration

COPY . .

EXPOSE 9997:9997

