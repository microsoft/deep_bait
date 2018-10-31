FROM tensorflow/tensorflow:latest-gpu-py3

RUN apt-get update && apt-get install -y --no-install-recommends \
        iproute2 \
        git \
        pandoc \
        locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip install fire toolz scikit-learn papermill
RUN git clone https://github.com/msalvaris/gpu_monitor.git && \
	pip install -r gpu_monitor/requirements.txt && \
	pip install -e gpu_monitor


