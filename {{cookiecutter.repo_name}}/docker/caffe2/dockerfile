FROM ufoym/deepo:caffe2-py36


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

RUN mkdir -p /src

RUN pip install --upgrade pip && \
    pip install Pillow scikit-learn notebook pandas matplotlib mkl nose pyyaml six h5py bcolz && \
    pip install fire toolz==0.8.2 scikit-learn bokeh==0.12.6 pandas==0.19.1 pypandoc==1.4 influxdb==5.0.0 requests>=2.17.0 pip==8.1.2 papermill && \
    pip install --upgrade requests && \
	git clone https://github.com/msalvaris/gpu_monitor.git && \
	pip install -r gpu_monitor/requirements.txt && \
	pip install --no-deps -e gpu_monitor

ENV PYTHONPATH='/src/:$PYTHONPATH'

WORKDIR /src
