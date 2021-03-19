PYTHON ?= python3
PREF_SHELL ?= bash
GITREF=$(shell git rev-parse --short HEAD)
GITREF_FULL=$(shell git rev-parse HEAD)
AGAVE_CREDS ?= ${HOME}/.agave/current
PYTEST_OPTS ?= -s -vvv
PYTEST_DIR ?= tests/test_000_imports.py
DOT_ENV ?= ./.env

####################################
# Docker image & dist
####################################

VERSION = $(shell python setup.py --version)
PKG = $(shell python setup.py --name)
PKGL = $(shell echo $(PKG) | tr '[:upper:]' '[:lower:]')
IMAGE_ORG ?= enho
IMAGE_NAME ?= $(PKGL)
IMAGE_TAG ?= $(VERSION)
IMAGE_DOCKER ?= $(IMAGE_ORG)/$(IMAGE_NAME):$(IMAGE_TAG)

####################################
# Sanity checks
####################################
PROGRAMS := git docker $(PYTHON) singularity tox jq
.PHONY: $(PROGRAMS)
.SILENT: $(PROGRAMS)

docker:
	docker info 1> /dev/null 2> /dev/null && \
	if [ ! $$? -eq 0 ]; then \
		echo "\n[ERROR] Could not communicate with docker daemon. You may need to run with sudo.\n"; \
		exit 1; \
	fi
$(PYTHON) poetry singularity jq:
	$@ --help &> /dev/null; \
	if [ ! $$? -eq 0 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please install $@"; \
		exit 1; \
	fi
tox:
	$@ -h &> /dev/null; \
	if [ ! $$? -eq 0 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please pip install $@"; \
		exit 1; \
	fi
git:
	$@ -h &> /dev/null; \
	if [ ! $$? -eq 129 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please install $@"; \
		exit 1; \
	fi

####################################
# Build Docker image
####################################
.PHONY: sdist dist/$(PKG)-$(VERSION).tar.gz image shell tests pytest-docker pytest-native clean clean-tests

sdist: dist/$(PKG)-$(VERSION).tar.gz

dist/$(PKG)-$(VERSION).tar.gz: setup.py | $(PYTHON)
	$(PYTHON) $< sdist -q

image: Dockerfile dist/$(PKG)-$(VERSION).tar.gz | docker
	docker build --progress plain --build-arg SDIST=$(word 2, $^) -t $(IMAGE_DOCKER) -f $< .

public-image: Dockerfile.public dist/$(PKG)-$(VERSION).tar.gz | docker
	docker build -f Dockerfile.public --build-arg SDIST=$(word 2, $^) -t sd2e/reactors:standalone .

####################################
# Tests
####################################
.PHONY: pytest-native $(DOT_ENV)

$(DOT_ENV): | jq
	$(PREF_SHELL) scripts/get_agave_creds.sh > $@

pytest-docker: clean image | docker
	docker run --rm -t \
		-v ${HOME}/.agave:/root/.agave \
		-v ${PWD}/tests/data/abacoschemas:/schemas:ro \
		-v ${PWD}/tests/data/message.jsonschema:/message.jsonschema:ro \
		$(IMAGE_DOCKER) \
		python3 -m pytest $(PYTEST_OPTS) /$(PKG)-$(VERSION)/$(PYTEST_DIR)
		#--env-file $(word 2, $^) \

pytest-native: clean | $(PYTHON)
	PYTHONPATH=./src $(PYTHON) -m pytest $(PYTEST_OPTS) $(PYTEST_DIR)

tests: pytest-native

shell: image | docker
	docker run --rm -it \
	-v ${HOME}/.agave:/root/.agave \
		-v ${PWD}/tests/data/abacoschemas:/schemas:ro \
		-v ${PWD}/tests/data/message.jsonschema:/message.jsonschema:ro \
	$(IMAGE_DOCKER) bash

clean: clean-tests

clean-rmi: image | docker
	echo "Not implemented" && exit 1
	#docker rmi -f $$(docker images -q --filter=reference="$(IMAGE_ORG)/$(IMAGE_NAME):*" --filter "before=$(IMAGE_DOCKER)")

clean-tests:
	rm -rf .hypothesis .pytest_cache __pycache__ */__pycache__ tmp.* *junit.xml

####################################
# Sphinx Docs
####################################
.PHONY: docs

docs:
	cd docsrc && make html
