# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Ivan Nardini <ivan.nardini@sas.com>"
LABEL description="The Jupyter Notebook Scientific Python Stack \
from https://github.com/jupyter/docker-stacks modified by Ivan Nardini \ 
to enable XGboost Python library"

USER root

# ffmpeg for matplotlib anim
RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Install Python 3 packages
RUN conda update --quiet --yes -n base conda && conda install --quiet --yes \
    'beautifulsoup4=4.8.*' \
    'conda-forge::blas=*=openblas' \
    'bokeh=1.3*' \
    'cloudpickle=1.2*' \
    'cython=0.29*' \
    'dask=2.2.*' \
    'dill=0.3*' \
    'h5py=2.9*' \
    'hdf5=1.10*' \
    'inflection' \
    'ipywidgets=7.5*' \
    'matplotlib-base=3.1.*' \
    'numba=0.45*' \
    'numexpr=2.6*' \
    'pandas=0.25*' \
    'patsy=0.5*' \
    'pymongo' \
    'protobuf=3.9.*' \
    'scikit-image=0.15*' \
    'scikit-learn=0.21*' \
    'scipy=1.3*' \
    'seaborn=0.9*' \
    'sqlalchemy=1.3*' \
    'statsmodels=0.10*' \
    'sympy=1.4*' \
    'vincent=0.4.*' \
    'xlrd' \
    && \
    conda clean --all -f -y && \
    # Activate ipywidgets extension in the environment that runs the notebook server
    jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    # Also activate ipywidgets extension for JupyterLab
    # Check this URL for most recent compatibilities
    # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
    pip install nbgitpuller && \
    jupyter serverextension enable --py nbgitpuller --sys-prefix && \
    pip install jupyterlab-git && \
    jupyter serverextension enable --py jupyterlab_git && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager@^1.0.1 --no-build && \
    jupyter labextension install @jupyterlab/git --no-build && \
    jupyter labextension install jupyterlab_bokeh@1.0.0 --no-build && \
    jupyter lab build && \
    npm cache clean --force && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    rm -rf /home/$NB_USER/.node-gyp && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

ENV NBGITPULLER_APP lab

# Install facets which does not have a pip or conda package at the moment
RUN cd /tmp && \
    git clone https://github.com/PAIR-code/facets.git && \
    cd facets && \
    jupyter nbextension install facets-dist/ --sys-prefix && \
    cd && \
    rm -rf /tmp/facets && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# USER root

# USER $NB_UID --> it's ok with root but some warning try NB_UID

# Install XGBoost library --> some issue with installation. I use pip
# RUN cd /etc &&\
#     git clone --recursive https://github.com/dmlc/xgboost && \
#     chmod -R 777 xgboost &&\
#     cd xgboost && \
#     make -j4 && \
#     cd python-package; python setup.py install

RUN pip install xgboost

# Install SAS Swat package
RUN pip install swat

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/ &&

RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
    fix-permissions /home/$NB_USER

USER $NB_UID