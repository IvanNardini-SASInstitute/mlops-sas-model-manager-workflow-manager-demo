FROM conda/miniconda3:latest

LABEL description="A container for Unit test"

USER root

RUN pip install --upgrade pip; \
    pip install dill numpy jsonify pandas scipy sklearn; \
    pip install unittest2

WORKDIR /home/unittest

COPY . .