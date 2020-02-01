FROM mongo

LABEL maintainer="Ivan Nardini <ivan.nardini@sas.com>"
LABEL description="A container for seed the Mondodb"

COPY ./sample.csv /data/db/sample.csv

CMD mongoimport -v --host mongo --db training_database --collection churn_data --type csv --file /data/db/sample.csv --headerline

# EXPOSE 27017