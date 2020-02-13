# The binary to build (just the basename).
MODULE := backend

# Where to push the docker image.
REGISTRY ?=

IMAGE := $(REGISTRY)/$(MODULE)

# This version-strategy uses git tags to set the version string
TAG := $(shell git describe --tags --always --dirty)

BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Suppress console spam
.SILENT:

init:
	apt update
	# Install python and package installer
	apt install python3 python3-pip
	# Install python package dependencies
	pip3 install -r requirements.txt
	# Install database dependencies
	apt install mysql-server python-mysqldb
	# Update system locales
	apt install locales-all
	# Install linter tools
	apt install flake8 bandit

db:
	sudo ./setup_db.sh

run:
	python3 -m $(MODULE)

test:
	pytest

lint:
	echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	pylint --rcfile=setup.cfg **/*.py
	echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	flake8
	echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	bandit -r --ini setup.cfg

# Example: make push VERSION=0.0.2
push: build-prod
	echo "\n${BLUE}Pushing image to GitHub Docker Registry...${NC}\n"
	docker push $(IMAGE):$(VERSION)

version:
	echo $(TAG)

.PHONY: clean image-clean build-prod push test

clean:
	rm -rf .pytest_cache .coverage .pytest_cache coverage.xml
