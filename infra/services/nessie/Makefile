# Makefile for Nessie deployment on Kubernetes
.DEFAULT_GOAL := help

# Variables (allow overriding)
NAMESPACE ?= lakehouse
NESSIE_OPERATOR ?= nessie-metastore/nessie

# Define phony targets
.PHONY: install-nessie uninstall-nessie help

# Install Nessie
install-nessie:
	@set -ex; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values infra/services/nessie/values.yaml \
		nessie $(NESSIE_OPERATOR)

# Uninstall Nessie
uninstall-nessie:
	@set -ex; \
	helm uninstall --namespace $(NAMESPACE) \
		nessie


# Show help message
help:
	@echo "Makefile commands:"
	@echo "  install-nessie: Install Nessie on Kubernetes"
	@echo "  uninstall-nessie: Uninstall Nessie from Kubernetes"