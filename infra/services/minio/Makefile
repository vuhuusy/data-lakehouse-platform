.DEFAULT_GOAL := help

# Variables
NAMESPACE ?= lakehouse
MINIO_OPERATOR ?= minio-operator/operator
MINIO_TENANT ?= minio-operator/tenant
MINIO_DIR ?= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Define phony targets
.PHONY: install-minio install-operator install-tenant \
		uninstall-minio uninstall-operator uninstall-tenant \
		help

# Install MinIO Operator and MinIO Tenant
install-minio: install-operator install-tenant

# Uninstall MinIO Operator and MinIO Tenant
uninstall-minio: uninstall-tenant uninstall-operator

# Install MinIO Operator
install-operator:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values $(MINIO_DIR)/operator/values.yaml \
		minio-operator $(MINIO_OPERATOR)

# Install MinIO Tenant
install-tenant:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values $(MINIO_DIR)/tenant/values.yaml \
		minio-tenant $(MINIO_TENANT)

# Uninstall MinIO Operator
uninstall-operator:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		minio-operator

# Uninstall MinIO Tenant
uninstall-tenant:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		minio-tenant

# Generate self-signed certificate
generate-self-signed-cert:
	@set -e; \
	openssl req -new -x509 -nodes -days 730 -keyout $(MINIO_DIR)/selfsigned.key \
		-out $(MINIO_DIR)/selfsigned.crt \
		-config $(MINIO_DIR)/openssl.conf

# Register self-signed certificate
register-self-signed-cert:
	@set -e; \
	kubectl delete secret minio-selfsigned-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret tls minio-selfsigned-secret \
		--key $(MINIO_DIR)/selfsigned.key \
		--cert $(MINIO_DIR)/selfsigned.crt \
		--namespace $(NAMESPACE); \
	kubectl delete secret operator-ca-tls --namespace $(NAMESPACE) || true; \
	kubectl create secret generic operator-ca-tls \
   		--from-file=public.crt=$(MINIO_DIR)/selfsigned.crt \
		--from-file=private.key=$(MINIO_DIR)/selfsigned.key \
		--namespace $(NAMESPACE)

# Show help message
help:
	@echo "Makefile commands:"
	@echo "make install-minio       - Install MinIO Operator and Tenant"
	@echo "make uninstall-minio     - Uninstall MinIO Operator and Tenant"
	@echo "make install-operator    - Install MinIO Operator"
	@echo "make install-tenant      - Install MinIO Tenant"
	@echo "make uninstall-operator  - Uninstall MinIO Operator"
	@echo "make uninstall-tenant    - Uninstall MinIO Tenant"
	@echo "make generate-self-signed-cert - Generate a self-signed certificate"
	@echo "make register-self-signed-cert - Register the self-signed certificate with Kubernetes"
