FROM conda/miniconda3:latest

LABEL description="A container for Unit test"

USER root

RUN pip install --upgrade pip; \
    # pip install dill numpy jsonify pandas scipy sklearn; \
    # # sklearn
    # pip install -U scikit-learn==0.21.3; \
    # pip install pytest
    pip install dill==0.3.1.1 \
                numpy==1.17.5 \
                pandas==0.25.3 \
                scipy==1.3.3 \
                scikit-image==0.15.0 \
                scikit-learn==0.21.3; \
    pip install xgboost; \
    pip install pytest;
    

WORKDIR /home/unittest

COPY . .