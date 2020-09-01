PYTHON ?= python3
PREF_SHELL ?= bash
GITREF=$(shell git rev-parse --short HEAD)
GITREF_FULL=$(shell git rev-parse HEAD)

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
DOCKER_OPTS ?= --rm -it

####################################
# Sanity checks
####################################

PROGRAMS := git docker $(PYTHON) singularity tox
.PHONY: $(PROGRAMS)
.SILENT: $(PROGRAMS)

docker:
	docker info 1> /dev/null 2> /dev/null && \
	if [ ! $$? -eq 0 ]; then \
		echo "\n[ERROR] Could not communicate with docker daemon. You may need to run with sudo.\n"; \
		exit 1; \
	fi
$(PYTHON) poetry singularity:
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
PYTEST_OPTS ?= -s -vvv
.PHONY: image shell tests tests-pytest clean clean-image clean-tests dist/$(PKG)-$(VERSION).tar.gz

dist/$(PKG)-$(VERSION).tar.gz: setup.py | $(PYTHON)
	$(PYTHON) setup.py sdist -q

image: Dockerfile dist/$(PKG)-$(VERSION).tar.gz requirements-stable.txt | docker
	cp $(word 2, $^) .
	docker build --build-arg SDIST=$(PKG)-$(VERSION) \
		--build-arg REQUIREMENTS=$(word 3, $^) \
		-t $(IMAGE_DOCKER) -f $< .
	rm $(word 2, $^) $(PKG)-$(VERSION).tar.gz

####################################
# Tests
####################################
.PHONY: pytest-native

tests: pytest-native

pytest-native: | $(PYTHON)
	PYTHONPATH=./src $(PYTHON) -m pytest $(PYTEST_OPTS)

shell: image | docker
	docker run --rm -it $(IMAGE_DOCKER) bash

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



