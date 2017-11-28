define PROJECT_HELP_MSG
Usage:
    make help                   show this message
    make all                    make docker image of all DL frameworks
    make build-all              push all docker images to docker hub
    make cntk                   make cntk BAIT image
    make push-cntk              push cntk BAIT image to docker hub
    make pytorch                make pytorch BAIT image
    make push-pytorch           push pytorch BAIT image to docker hub
    make keras                  make keras BAIT image
    make push-keras             push keras BAIT image to docker hub
    make chainer                make chainer BAIT image
    make push-chainer           push chainer BAIT image to docker hub
    make mxnet                  make mxnet BAIT image
    make push-mxnet             push mxnet BAIT image to docker hub
    make caffe2                 make caffe2 BAIT image
    make push-caffe2            push caffe2 BAIT image to docker hub
    make tf                     make tf BAIT image
    make push-tf                push tf BAIT image to docker hub
endef
export PROJECT_HELP_MSG

name_prefix:=masalvar

help:
	echo "$$PROJECT_HELP_MSG" | less

cntk:
	docker build -t $(name_prefix)/cntk_bait cntk

push-cntk:
	docker push $(name_prefix)/cntk_bait

pytorch:
	docker build -t $(name_prefix)/pytorch_bait pytorch

push-pytorch:
	docker push $(name_prefix)/pytorch_bait

keras:
	docker build -t $(name_prefix)/keras_bait keras

push-keras:
	docker push $(name_prefix)/keras_bait

chainer:
	docker build -t $(name_prefix)/chainer_bait chainer

push-chainer:
	docker push $(name_prefix)/chainer_bait

mxnet:
	docker build -t $(name_prefix)/mxnet_bait mxnet

push-mxnet:
	docker push $(name_prefix)/mxnet_bait

caffe2:
	docker build -t $(name_prefix)/caffe2_bait caffe2

push-caffe2:
	docker push $(name_prefix)/caffe2_bait

tf:
	docker build -t $(name_prefix)/tf_bait tensorflow

push-tf:
	docker push $(name_prefix)/tf_bait

all: cntk pytorch keras chainer mxnet caffe2 tf
	@echo 'Built all DL docker images'

push-all: all push-cntk push-pytorch push-keras push-chainer push-mxnet push-caffe2 push-tf
	@echo 'Pushed all DL docker images to $(name_prefix)'

.PHONY: help cntk pytorch keras chainer mxnet caffe2 tf all push-all push-cntk push-pytorch push-keras push-chainer push-mxnet push-caffe2 push-tf