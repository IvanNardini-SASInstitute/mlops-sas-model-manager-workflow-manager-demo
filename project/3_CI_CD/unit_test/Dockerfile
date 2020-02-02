FROM conda/miniconda3:latest

LABEL description="The basic python.3 image provided by SAS(R) for Open Source Scoring Container \
                    modified by Ivan Nardini for Unit Testing purposes"

USER root

RUN pip install --upgrade pip; \
    pip install dill numpy jsonify pandas scipy sklearn; \
    pip install unitest;

WORKDIR /unitest
