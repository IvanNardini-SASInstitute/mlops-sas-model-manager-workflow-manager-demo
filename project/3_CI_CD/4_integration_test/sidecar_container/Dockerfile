FROM conda/miniconda3:latest

LABEL description="The basic Python3 Score Box image provided by SAS(R) for Open Source Scoring Container"

USER root

RUN pip install --upgrade pip; \
    pip install dill==0.3.1.1 \
                numpy==1.17.5 \
                pandas==0.25.3 \
                scipy==1.3.3 \
                scikit-learn==0.21.3; \
    # pip install dill numpy jsonify pandas scipy sklearn; \
    pip install flask gunicorn; \
    pip install xgboost;

WORKDIR /pybox/app

COPY app    /pybox/app
COPY model  /pybox/model

EXPOSE 9999:9999
ENTRYPOINT ["/bin/bash", "startServer.sh"]  