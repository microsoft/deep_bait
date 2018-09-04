.ONESHELL:
SHELL := /bin/bash

define PROJECT_HELP_MSG
Usage:
	make help                           show this message
	make exec-cntk                      test cntk notebook locally in docker container
	make exec-pytorch                   test pytorch notebook locally in docker container
	make exec-keras-tf                  test keras tf notebook locally in docker container
	make exec-keras-cntk                test keras cntk notebook locally in docker container
	make exec-chainer                   test chainer notebook locally in docker container
	make exec-mxnet                     test mxnet notebook locally in docker container
	make exec-caffe2                    test caffe2 notebook locally in docker container
	make exec-tf                        test tf notebook locally in docker container
	make exec-gluon                     test gluon notebook locally in docker container
	cntk-nb-server                      run cntk docker container jupyter notebook server
	pytorch-nb-server                   run pytoch docker container jupyter notebook server
	keras-nb-server                     run keras docker container jupyter notebook server
	chainer-nb-server                   run chainer docker container jupyter notebook server
	mxnet-nb-server                     run mxnet docker container jupyter notebook server
	caffe2-nb-server                    run caffe2 docker container jupyter notebook server
	tf-nb-server                        run tf docker container jupyter notebook server
	gluon-nb-server                     run gluon docker container jupyter notebook server

By default nvidia-docker and gpu will be used, use argument GPU=0 to use docker
endef
export PROJECT_HELP_MSG

GPU?=1
DOCKER:=nvidia-docker

ifeq ($(GPU), 0)
	DOCKER:=docker
endif

CNTK_IMAGE:="masalvar/cntk_bait"
PYTORCH_IMAGE:="masalvar/pytorch_bait"
KERAS_IMAGE:="masalvar/keras_bait"
CHAINER_IMAGE="masalvar/chainer_bait"
MXNET_IMAGE="masalvar/mxnet_bait"
CAFFE2_IMAGE="masalvar/caffe2_bait"
TF_IMAGE="masalvar/tf_bait"

define prepare_scripts
 mkdir -p temp
 mkdir -p temp/model
 mkdir -p temp/output
endef

DATA_DIR:=$(shell dirname $(DATA))
PWD:=$(shell pwd)
PROJ_ROOT:=$(shell dirname $(PWD))
setup_volumes:=-v $(PROJ_ROOT)/exec_src:/mnt/script \
	-v $(DATA_DIR):/mnt/input \
	-v $(PWD)/temp/model:/mnt/model \
	-v $(PWD)/temp/output:/mnt/output

setup_environment:=--env AZ_BATCHAI_INPUT_DATASET='/mnt/input' \
	--env AZ_BATCHAI_INPUT_SCRIPT='/mnt/script' \
	--env AZ_BATCHAI_OUTPUT_MODEL='/mnt/model' \
	--env AZ_BATCHAI_MOUNT_ROOT='/mnt/output'

prepare_data:= chmod +x /mnt/script/prepare_data.sh && \
	/mnt/script/prepare_data.sh

define serve_notebbook
 $(prepare_scripts)
 nvidia-docker run -it \
 $(setup_volumes) \
 $(setup_environment) \
 -p 9999:9999 \
 $(1) bash -c "\
 $(prepare_data) && \
 $(2) \
 jupyter notebook --port=9999 --ip=* --allow-root --no-browser --notebook-dir=/mnt/script"
endef

define execute_notebook
 $(prepare_scripts)
 nvidia-docker run -it \
 $(setup_volumes) \
 $(setup_environment) \
 $(1) bash -c "\
 $(prepare_data) && \
 $(2) \
 cd /mnt/script && \
 papermill $(3) --no-progress-bar"
endef

help:
	@echo "$$PROJECT_HELP_MSG" | less


exec-cntk:
	$(call execute_notebook, $(CNTK_IMAGE), source /cntk/activate-cntk &&, CNTK_CIFAR.ipynb /mnt/output/CNTK_NEW.ipynb -p EPOCHS 10)

exec-pytorch:
	$(call execute_notebook, $(PYTORCH_IMAGE), source activate pytorch-py35 &&, PyTorch_CIFAR.ipynb /mnt/output/PyTorch_NEW.ipynb -p EPOCHS 10)

exec-keras-cntk:
	$(call execute_notebook, $(KERAS_IMAGE), , Keras_CNTK_CIFAR.ipynb /mnt/output/Keras_CNTK_NEW.ipynb -p EPOCHS 10)

exec-keras-tf:
	$(call execute_notebook, $(KERAS_IMAGE), , Keras_TF_CIFAR.ipynb /mnt/output/Keras_TF_NEW.ipynb -p EPOCHS 10)

exec-chainer:
	$(call execute_notebook, $(CHAINER_IMAGE), , Chainer_CIFAR.ipynb /mnt/output/Chainer_NEW.ipynb -p EPOCHS 10 )

exec-mxnet:
	$(call execute_notebook, $(MXNET_IMAGE), , MXNet_CIFAR.ipynb /mnt/output/MXNet_NEW.ipynb python3 -p EPOCHS 10)

exec-caffe2:
	$(call execute_notebook, $(CAFFE2_IMAGE), , Caffe2_CIFAR.ipynb /mnt/output/Caffe2_NEW.ipynb python3 -p EPOCHS 10)

exec-tf:
	$(call execute_notebook, $(TF_IMAGE), , Tensorflow_CIFAR.ipynb /mnt/output/Tensorflow_NEW.ipynb python3 -p EPOCHS 10)

exec-gluon:
	$(call execute_notebook, $(MXNET_IMAGE), , Gluon_CIFAR.ipynb /mnt/output/Gluon_NEW.ipynb python3 -p EPOCHS 10)


exec-all: exec-cntk exec-pytorch exec-keras-cntk exec-keras-tf exec-chainer exec-mxnet exec-caffe2 exec-tf exec-gluon
	@echo 'Run all models'


cntk-nb-server:
	$(call serve_notebbook, $(CNTK_IMAGE), source /cntk/activate-cntk &&)


pytorch-nb-server:
	$(call serve_notebbook, $(PYTORCH_IMAGE),source activate pytorch-py35 && )


keras-nb-server:
	$(call serve_notebbook, $(KERAS_IMAGE), )


chainer-nb-server:
	$(call serve_notebbook, $(CHAINER_IMAGE), )


mxnet-nb-server:
	$(call serve_notebbook, $(MXNET_IMAGE), )


caffe2-nb-server:
	$(call serve_notebbook, $(CAFFE2_IMAGE), )


tf-nb-server:
	$(call serve_notebbook, $(TF_IMAGE), )


gluon-nb-server:
	$(call serve_notebbook, $(MXNET_IMAGE), )

.PHONY: help
