.ONESHELL:
SHELL := /bin/bash

define PROJECT_HELP_MSG
Usage:
	make help                           show this message
	make initial-setup                  setup environment
	make clean							clean up the project and remove environment
endef
export PROJECT_HELP_MSG


help:
	@echo "$$PROJECT_HELP_MSG" | less


initial-setup: install-az-cli install-blobxfer select-subscription register-azb create-service-principal create-storage create-fileshare set-storage-key transfer-to-fileshare
	@echo "Setup complete"

install-blobxfer:
	pip install blobxfer==1.0.0

install-az-cli:
	pip install azure-cli

register-azb:
	az provider register -n Microsoft.Batch
	az provider register -n Microsoft.BatchAI

create-service-principal:
	$(eval app_id:=$(shell az ad sp create-for-rbac --name $(SERVICE_PRINCIPAL_APP_NAME) --password $(SERVICE_PRINCIPAL_PWD) |jq '.["appId"]'))
	$(eval subscription_id:=$(shell az account show |jq '.["id"]'))
	$(eval tenant:=$(shell az account show |jq '.["tenantId"]'))
	anaconda-project add-variable APP_ID
	anaconda-project set-variable APP_ID=$(app_id)
	anaconda-project add-variable TENANT
	anaconda-project set-variable TENANT=$(tenant)
	anaconda-project add-variable SUBSCRIPTION_ID
	anaconda-project set-variable SUBSCRIPTION_ID=$(subscription_id)

select-subscription:
	az login -o table
	az account set --subscription "$(SELECTED_SUBSCRIPTION)"

create-storage:
	@echo "Creating storage account"
	az group create -n $(GROUP_NAME) -l $(LOCATION) -o table
	az storage account create -l $(LOCATION) -n $(STORAGE_ACCOUNT_NAME) -g $(GROUP_NAME) --sku Standard_LRS

set-storage:
	$(eval azure_storage_key:=$(shell az storage account keys list -n $(STORAGE_ACCOUNT_NAME) -g $(GROUP_NAME) | jq '.[0]["value"]'))
	$(eval azure_storage_account:= $(STORAGE_ACCOUNT_NAME))
	$(eval file_share_name:= $(FILE_SHARE_NAME))

create-fileshare: set-storage
	@echo "Creating fileshare"
	az storage share create -n $(file_share_name) --account-name $(azure_storage_account) --account-key $(azure_storage_key)

transfer-to-fileshare: set-storage prepare-data
	@echo "Transfering data to fileshare"
	blobxfer upload --mode file --storage-account-key $(azure_storage_key) --storage-account $(azure_storage_account) --remote-path $(file_share_name)/data --local-path $(shell dirname $(DATA))

set-storage-key: set-storage
	@echo "Setting storage account key"
	anaconda-project add-variable STORAGE_ACCOUNT_KEY
	anaconda-project set-variable STORAGE_ACCOUNT_KEY=$(azure_storage_key)

prepare-data:
	tar xzvf $(DATA) --directory $(shell dirname $(DATA))

clean:
	anaconda-project remove-variable STORAGE_ACCOUNT_KEY
	anaconda-project remove-variable APP_ID
	anaconda-project remove-variable TENANT
	anaconda-project remove-variable SUBSCRIPTION_ID
	rm -rf envs data anaconda-project-local.yml


.PHONY: help initial-setup install-blobxfer install-az-cli register-azb create-service-principal select-subscription create-storage set-storage create-fileshare transfer-to-fileshare set-storage-key prepare-data clean
