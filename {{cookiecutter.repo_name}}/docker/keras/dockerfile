FROM nvidia/cuda:8.0-cudnn6-devel
# Based on dockerfile from https://github.com/fchollet/keras/tree/master/docker

RUN apt-get update && apt-get install -y --no-install-recommends \
        iproute2 \
        git \
        locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH

RUN mkdir -p $CONDA_DIR && \
    echo export PATH=$CONDA_DIR/bin:'$PATH' > /etc/profile.d/conda.sh && \
    apt-get update && \
    apt-get install -y wget git libhdf5-dev g++ graphviz openmpi-bin && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo "c59b3dd3cad550ac7596e0d599b91e75d88826db132e4146030ef471bb434e9a *Miniconda3-4.2.12-Linux-x86_64.sh" | sha256sum -c - && \
    /bin/bash /Miniconda3-4.2.12-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh

# Python
ARG python_version=3.5

ENV PATH /opt/conda/envs/py$PYTHON_VERSION/bin:$PATH

RUN mkdir -p /src

RUN conda install -y python=${python_version} && \
    pip install --upgrade pip && \
    pip install tensorflow-gpu==1.4.1 && \
    pip install https://cntk.ai/PythonWheel/GPU/cntk-2.3-cp35-cp35m-linux_x86_64.whl && \
    conda install Pillow scikit-learn notebook pandas matplotlib mkl nose pyyaml six h5py && \
    conda install pygpu bcolz && \
    pip install fire toolz==0.8.2 scikit-learn bokeh==0.12.6 pandas==0.19.1 pypandoc==1.4 influxdb==5.0.0 requests>=2.17.0 pip==8.1.2 papermill && \
    pip install --upgrade requests && \
    pip install keras==2.1.2 && \
	git clone https://github.com/msalvaris/gpu_monitor.git && \
	pip install -r gpu_monitor/requirements.txt && \
	pip install --no-deps -e gpu_monitor && \
    conda clean -yt

ENV LD_LIBRARY_PATH=/opt/conda/lib:/usr/local/nvidia/lib64

ENV PYTHONPATH='/src/:$PYTHONPATH'

WORKDIR /src

