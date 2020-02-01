FROM python:3

WORKDIR /usr/src/app

RUN pip install pylint

COPY ./project/3_CI_CD/code_quality_test .

# CMD [ "pylint", "./tests/wrong.py" ]