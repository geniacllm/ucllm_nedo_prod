include .env
export

SHELL := $(shell which bash) # Use bash syntax to be consistent

OS_NAME := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH_NAME_RAW := $(shell uname -m)

COMMIT=$$(git describe --tags --always)

LOCAL_BIN:=$(CURDIR)/bin
PATH:=$(LOCAL_BIN):$(PATH)


# 'make' command will trigger the help target
.DEFAULT_GOAL := help

help: ## Display this help screen
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


# utils
cmd-exists-%:
	@hash $(*) > /dev/null 2>&1 || (echo "ERROR: '$(*)' must be installed and available on your PATH."; exit 1)

guard-%:
	@if [ -z '${${*}}' ]; then echo 'ERROR: environment variable $* not set' && exit 1; fi


# this repository specific
start: cmd-exists-code ## Open this repository with VSCode
	@code vscode.code-workspace
.PHONY: start

# check set
check-path:  ## Check PATH
	@echo $${PATH//:/\\n}
.PHONY: check-path

check-myip: ## Check my ip address
	@ifconfig | sed -En "s/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p"
.PHONY: check-myip

check-dockerport: cmd-exists-docker cmd-exists-jq ## Check docker port
	@docker ps -q | xargs docker inspect | jq '.[] | {name: .Name, ports: .NetworkSettings.Ports}'

# version checks
check-version-python: cmd-exists-python3 guard-EXPECTED_PYTHON_VERSION  ## Check Python version
	@version=$$(python3 --version 2>&1 | awk '{print $$2}') ; \
	if [ "$$version" != "$(EXPECTED_PYTHON_VERSION)" ]; then \
		echo "ERROR: Expected Python version $(EXPECTED_PYTHON_VERSION), but found $$version"; \
		exit 1; \
	fi
.PHONY: check-version-python

check-version-nvcc: cmd-exists-nvcc guard-EXPECTED_NVCC_VERSION  ## Check NVCC version
	@version=$$(nvcc --version | grep "release" | awk '{print $$6}' | cut -d ',' -f 1) ; \
	if [ "$$version" != "$(EXPECTED_NVCC_VERSION)" ]; then \
		echo "ERROR: Expected NVCC version $(EXPECTED_NVCC_VERSION), but found $$version"; \
		exit 1; \
	fi
.PHONY: check-version-nvcc

check-version-conda: cmd-exists-conda guard-EXPECTED_CONDA_VERSION  ## Check Conda version
	@version=$$(conda --version 2>&1 | awk '{print $$2}') ; \
	if [ "$$version" != "$(EXPECTED_CONDA_VERSION)" ]; then \
		echo "ERROR: Expected Conda version $(EXPECTED_CONDA_VERSION), but found $$version"; \
		exit 1; \
	fi
.PHONY: check-version-conda

check-version-torch: cmd-exists-python guard-EXPECTED_TORCH_VERSION  ## Check PyTorch version
	@version=$$(python3 -c "import torch; print(torch.__version__)" 2>/dev/null) ; \
	if [ -z "$$version" ]; then \
		echo "ERROR: PyTorch is not installed"; \
		exit 1; \
	elif [ "$$version" != "$(EXPECTED_TORCH_VERSION)" ]; then \
		echo "ERROR: Expected PyTorch version $(EXPECTED_TORCH_VERSION), but found $$version"; \
		exit 1; \
	fi
.PHONY: check-version-torch

check-versions-for-llm:  ## Check versions for LLM
	@$(MAKE) check-version-python
	@$(MAKE) check-version-nvcc
	@$(MAKE) check-version-conda
	@$(MAKE) check-version-torch
.PHONY: check-versions-for-llm