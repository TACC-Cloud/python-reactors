PYTHON ?= python3
PREF_SHELL ?= bash
GITREF=$(shell git rev-parse --short HEAD)
GITREF_FULL=$(shell git rev-parse HEAD)
PYTEST_OPTS ?= -k 'not loggly_auth'
PYTEST_DIR ?= tests
DOT_ENV ?= ./.env

####################################
# Docker image & dist
####################################

VERSION = $(shell poetry version --short)
PKG = $(shell poetry version | awk '{print $$1}')
PKGL = $(shell echo $(PKG) | tr '[:upper:]' '[:lower:]')
IMAGE_ORG ?= tacc
IMAGE_NAME ?= $(PKGL)
IMAGE_TAG ?= $(VERSION)
IMAGE_DOCKER ?= $(IMAGE_ORG)/$(IMAGE_NAME):$(IMAGE_TAG)

####################################
# Build Docker image
####################################
.PHONY: image build

build:
	rm -rf dist
	poetry build

image: Dockerfile build
	docker build -t $(IMAGE_DOCKER) -f $< .

####################################
# Tests
####################################
.PHONY: pytest-docker test-cli-docker tests shell clean 

tests: pytest-native test-cli-docker pytest-docker 

pytest-native tox:
	tox -- $(PYTEST_OPTS) $(PYTEST_DIR)

pytest-docker: clean image 
	docker run --rm -t \
		-v ${HOME}/.agave:/root/.agave \
		-v ${PWD}/tests/data/abacoschemas:/schemas:ro \
		-v ${PWD}/tests/data/message.jsonschema:/message.jsonschema:ro \
		-v ${PWD}/$(PYTEST_DIR):/mnt/ephemeral-01/$(PYTEST_DIR) \
		$(IMAGE_DOCKER) \
		bash -c "(python3 -m pip install -q pytest polling2 && python3 -m pytest $(PYTEST_OPTS) /mnt/ephemeral-01/$(PYTEST_DIR))"

test-cli-docker: clean image 
	docker run --rm -t \
		-v ${HOME}/.agave:/root/.agave \
		$(IMAGE_DOCKER) \
		bash -c "(python3 -m reactors.cli usage && python3 -m reactors.cli run)"

shell: image 
	docker run --rm -it \
	-v ${HOME}/.agave:/root/.agave \
		-v ${PWD}/tests/data/abacoschemas:/schemas:ro \
		-v ${PWD}/tests/data/message.jsonschema:/message.jsonschema:ro \
	$(IMAGE_DOCKER) bash

clean: 
	rm -rf .hypothesis .pytest_cache __pycache__ */__pycache__ tmp.* *junit.xml

####################################
# Sphinx Docs
####################################
.PHONY: docs

docs:
	cd docsrc && make html

livehtml:
	cd docsrc && make livehtml
