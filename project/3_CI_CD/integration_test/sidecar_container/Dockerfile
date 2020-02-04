FROM conda/miniconda3:latest

LABEL description="The basic Python3 Score Box image provided by SAS(R) for Open Source Scoring Container"

USER root

RUN pip install --upgrade pip; \
    pip install dill numpy jsonify pandas scipy sklearn; \
    pip install flask gunicorn; 

WORKDIR /pybox/app

COPY app    /pybox/app
COPY model  /pybox/model

EXPOSE 8080:8080
ENTRYPOINT ["/bin/bash", "startServer.sh"]