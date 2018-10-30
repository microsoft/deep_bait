# Deep Learning Frameworks using Azure Batch AI
## Introduction
This repo contains everything you need to run some of the most popular deep learning frameworks on Batch AI. 
Batch AI is a service that allows you to run various machine learning workloads on clusters of VMs. For more details on the service please look [here](https://docs.microsoft.com/en-gb/azure/batch-ai/overview). 

This project uses [anaconda-project](https://github.com/Anaconda-Platform/anaconda-project) and makefiles to create the environment, download the data and prepare all necessary artifacts.

The frameworks are:
* [Caffe2](exec_src/Caffe2_CIFAR.ipynb)
* [MXNet (Gluon)](exec_src/MXNet_CIFAR.ipynb)
* [Gluon](exec_src/Gluon_CIFAR.ipynb)
* [PyTorch](exec_src/PyTorch_CIFAR.ipynb)
* [Chainer](exec_src/Chainer_CIFAR.ipynb)
* [Keras (TF)](exec_src/Keras_TF_CIFAR.ipynb)
* [Keras (CNTK)](exec_src/Keras_CNTK_CIFAR.ipynb)
* [Tensorflow](exec_src/Tensorflow_CIFAR.ipynb)
* [CNTK](exec_src/CNTK_CIFAR.ipynb)

Each of the notebooks trains a simple Convolution Neural Network on the CIFAR10 dataset.

## Setup
This project was developed and tested on an [Azure Ubuntu DSVM](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/microsoft-ads.linux-data-science-vm-ubuntu) but should be compatible with any Linux distribution. The prerequisites for this are:
* [Azure account](https://azure.microsoft.com/en-gb/free/)
* [Register for Batch AI](https://docs.microsoft.com/en-gb/azure/batch-ai/quickstart-python)
* [Cookiecutter installed](https://github.com/audreyr/cookiecutter) on VM or local machine
* Docker installed (only required for local testing and creating docker images)
* Install [jq](https://github.com/stedolan/jq) if not already installed
```bash
sudo apt-get install jq
```


##### Optional
If you want to execute docker without having to sudo each time then you need to run the following:
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```
You may need to log out and log back in again for changes to take effect. Instructions from https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user


## Setting up project
Once you have docker installed and anaconda-project you can start setting up the project.
Many of the interactions happen through anaconda-project and to list the available commands simply run:

```bash
cookiecutter https://github.com/Microsoft/deep_bait.git --checkout cookiecutter
```

When you first set the project you will need to set a number of things up. These are handled through cookiecutter, for options that you want to leave the same simply press enter. 
It will create the appropriate anaconda environment locally inside the envs folder. 
Once that is done activate the newly created conda env and run the initial-setup by running the commands below.
```bash
conda activate envs
make initial-setup
```
The above command will do the following:
* Install the Azure CLI
* Install Blobxfer
* Log you in to Azure and select the appropriate subscription
* Register for the appropriate services
* Create a service principal
* Create a storage account and fileshare
* Download the CIFAR data and upload it to the fileshare


The command can take a while. Pay attention since it will ask you to log in to your Azure account. If you want a better understanding of what is going on have a look at the [Makefile]({{cookiecutter.repo_name}}/Makefile)

## Run Batch AI
Instructions on how to setup the cluster and start submitting jobs are detailed in [ExploringBatchAI]({{cookiecutter.repo_name}}/ExploringBatchAI.ipynb) notebook. To start it run the following command: 

```bash
make notebook
```

We are assuming you are executing on a VM so it will not try to open up a browser. This will start a Jupyter notebook server that should be reachable the same way you would reach your standard Jupyter notebook server.
The above commands assumes that the appropriate ports are open on the VM and that the server has been set up to accept connections from any ip.


## Local Development
When executing jobs on services such as Batch AI it is important to iron out as many of the bugs before executing on the cluster. That is why with this project there is a folder called [local_test]({{cookiecutter.repo_name}}/local_test) that includes a Makefile that allows you to run notebook servers inside the containers as well as test the execution of the containers.

To run any of the notebooks:
```bash
cd local_test
make cntk-nb-server
```

The above command sets up the environment variables necessary and then executes the notebook server inside the CNTK docker container.
The above commands assumes that the appropriate ports are open on the VM and that the server has been set up to accept connections from any ip.

## Docker
The dockerfiles used to create the docker images can be found [here](docker). There is also a makefile in the folder that has all the commands for creating the docker images.

## Clean/Delete project
To clean the project and start from scratch or simply to remove the environment and data files simply run
```bash
make clean
```

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

