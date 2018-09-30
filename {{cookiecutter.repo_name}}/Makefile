.ONESHELL:
SHELL := /bin/bash

define PROJECT_HELP_MSG
Usage:
	make help                           show this message
	make initial-setup                  setup environment
	make clean							clean up the project and remove environment
endef
export PROJECT_HELP_MSG

DATA:={{cookiecutter.data_location}}/cifar-10-python.tar.gz

help:
	@echo "$$PROJECT_HELP_MSG" | less

###
# To set everything up run
# source activate envs
# make initial-setup
###

define denv
$(shell dotenv get $(1)|cut -f2 -d"=")
endef


initial-setup: install-az-cli install-blobxfer select-subscription register-azb create-service-principal create-storage create-fileshare set-storage-key transfer-to-fileshare
	@echo "Setup complete"


notebook:
	export $(dotenv list | xargs) && jupyter notebook --ip=* --port=9999 --no-browser


transfer-to-fileshare: set-storage download-data prepare-data
	@echo "Transfering data to fileshare"
	blobxfer upload --mode file --storage-account-key $(azure_storage_key) --storage-account $(azure_storage_account) --remote-path $(file_share_name)/data --local-path $(shell dirname $(DATA))


install-blobxfer:
	pip install blobxfer==1.4.0

install-az-cli:
	pip install azure-cli

register-azb:
	az provider register -n Microsoft.Batch
	az provider register -n Microsoft.BatchAI

get-password:
	$(eval pwd:=$(shell bash -c 'read -s -p "Enter password for service principal: " pwd; echo $$pwd'))
	dotenv set SERVICE_PRINCIPAL_PWD "$(pwd)"


#TODO: Add ability to use same app, find app by name and extract app id
#(envs) mat@mspony1:~/repos/dbait$ az ad sp list --display-name dbait --query "[0].[appId, appDisplayName]" -o json[  "2f610756-2c1a-4261-b530-5296fec1d6ca",  "dbaitapp"]

#TODO: Add ability to create grafana and influxdb locally


create-service-principal: get-password
	$(eval app_id:=$(shell az ad sp create-for-rbac --name $(call denv,SERVICE_PRINCIPAL_APP_NAME) --password $(call denv,SERVICE_PRINCIPAL_PWD) |jq '.["appId"]'))
	$(eval subscription_id:=$(shell az account show |jq '.["id"]'))
	$(eval tenant:=$(shell az account show |jq '.["tenantId"]'))
	dotenv set APP_ID $(app_id) 
	dotenv set TENANT $(tenant) 
	dotenv set SUBSCRIPTION_ID $(subscription_id) 

select-subscription:
	list=`az account list -o table`
	@if [ "$list" == '[]' ] || [ "$list" == '' ]; then 
	  @az login -o table
	@else
	  @az account list -o table 
	@fi
	az account set --subscription "$(call denv,SELECTED_SUBSCRIPTION)"

create-storage:
	@echo "Creating storage account"
	az group create -n $(call denv,GROUP_NAME) -l $(call denv,LOCATION) -o table
	az storage account create -l $(call denv,LOCATION) -n $(call denv,STORAGE_ACCOUNT_NAME) -g $(call denv,GROUP_NAME) --sku Standard_LRS

set-storage:
	$(eval azure_storage_key:=$(shell az storage account keys list -n $(call denv,STORAGE_ACCOUNT_NAME) -g $(call denv,GROUP_NAME) | jq '.[0]["value"]'))
	$(eval azure_storage_account:= $(call denv,STORAGE_ACCOUNT_NAME))
	$(eval file_share_name:= $(call denv,FILE_SHARE_NAME))

create-fileshare: set-storage
	@echo "Creating fileshare"
	az storage share create -n $(file_share_name) --account-name $(azure_storage_account) --account-key $(azure_storage_key)

download-data:
	wget http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz -P $(shell dirname $(DATA))

set-storage-key: set-storage
	@echo "Setting storage account key"
	dotenv set STORAGE_ACCOUNT_KEY "$(azure_storage_key)" 

prepare-data:
	tar xzvf $(DATA) --directory $(shell dirname $(DATA))

create-env:
	mkdir -p envs
	conda env create --file environment.yml -p $(shell readlink -f envs)

clean:
	rm -rf envs data .env

delete-service-principal:
	az ad sp delete --id $(call denv,APP_ID)

delete-group:
	az group delete -n $(call denv,GROUP_NAME)



.PHONY: help initial-setup install-blobxfer install-az-cli register-azb create-service-principal select-subscription create-storage set-storage create-fileshare transfer-to-fileshare set-storage-key prepare-data clean
