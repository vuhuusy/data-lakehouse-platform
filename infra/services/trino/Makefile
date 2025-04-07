# Makefile for Trino deployment on Kubernetes
.DEFAULT_GOAL := help

# Variables (allow overriding)
NAMESPACE ?= lakehouse
TRINO_OPERATOR ?= trino/trino

# Define phony targets
.PHONY: install-trino uninstall-trino help

build-trino-custom-dockerfile:
	@set -ex; \
	docker build --progress=plain \
		-t huusy/trino:470 \
		-f infra/services/trino/Dockerfile .

release-docker-images:
	@set -ex; \
	docker push huusy/trino:470

# Install Trino
install-trino:
	@set -ex; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values infra/services/trino/values.yaml \
		trino $(TRINO_OPERATOR)

# Uninstall Trino
uninstall-trino:
	@set -ex; \
	helm uninstall --namespace $(NAMESPACE) \
		trino

# Show help message
help:
	@echo "Makefile commands:"
	@echo "  install-trino     Install Trino on Kubernetes"
	@echo "  uninstall-trino   Uninstall Trino from Kubernetes"
	@eoch "  build-trino-custom-dockerfile   Build custom Trino Docker image"
	@echo "  release-docker-images   Release custom Trino Docker image"