.DEFAULT_GOAL := help

# Variables
NAMESPACE ?= lakehouse
NIFI_OPERATOR ?= cetic/nifi

# Define phony targets
.PHONY: build-nifi-custom-image release-docker-images \
		install-cert-manager uninstall-cert-manager \
		install-nifi uninstall-nifi \
		help

# Build NiFi custom image
build-nifi-custom-image:
	@set -e; \
	docker build --progress=plain \
		-t huusy/nifi1:1.23.2 \
		-f infra/services/nifi/Dockerfile .

# Push NiFi custom image
release-docker-images:
	@set -e; \
	docker push huusy/nifi1:1.23.2

# Install NiFi
install-nifi:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values infra/services/nifi/values.yaml \
		nifi $(NIFI_OPERATOR)

# Uninstall NiFi
uninstall-nifi:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		nifi

# Install certManager
install-cert-manager:
	@set -e; \
	helm upgrade --install --namespace ${NAMESPACE} \
		cert-manager jetstack/cert-manager \
		--set installCRDs=true

# Uninstall certManager
uninstall-cert-manager:
	@set -e; \
	helm uninstall --namespace ${NAMESPACE} \
		cert-manager

# Show help message
help:
	@echo "Makefile commands:"
	@echo "  build-nifi-custom-image  Build NiFi custom Docker image"
	@echo "  release-docker-images    Push NiFi custom Docker image to registry"
	@echo "  install-nifi             Install NiFi on Kubernetes"
	@echo "  uninstall-nifi           Uninstall NiFi from Kubernetes"
	@echo "  install-cert-manager     Install cert-manager on Kubernetes"
	@echo "  uninstall-cert-manager   Uninstall cert-manager from Kubernetes"
