.DEFAULT_GOAL := help

NAMESPACE ?= minio
MINIO_OPERATOR ?= minio-operator/operator
MINIO_TENANT ?= minio-operator/tenant

.PHONY: install uninstall \
		install-operator install-tenant \
		uninstall-operator uninstall-tenant \
		generate-self-signed-cert register-self-signed-cert  \
		create-namespace  \
		create-nodeport  \
		delete-nodeport  \
		help

install: create-namespace install-operator install-tenant

uninstall: uninstall-tenant uninstall-operator delete-nodeport

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-operator:
	@set -e; \
	@echo "Installing MinIO Operator..."
	helm repo list | grep -q minio-operator || helm repo add minio-operator https://operator.min.io
	helm repo update

	helm upgrade --install minio-operator $(MINIO_OPERATOR) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/minio/operator/values.yaml \
	
	@echo "MinIO Operator installation complete!"

install-tenant:
	@set -e; \
	@echo "Installing MinIO Tenant..."
	helm upgrade --install minio-tenant $(MINIO_TENANT) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/minio/tenant/values.yaml

	@echo "MinIO Tenant installation complete!"

uninstall-operator:
	@set -e; \
	@echo "Uninstalling MinIO Operator..."
	kubectl delete secret minio-selfsigned-secret --namespace $(NAMESPACE) || true
	helm uninstall --namespace $(NAMESPACE) \
		minio-operator
	@echo "MinIO Operator uninstallation complete!"

uninstall-tenant:
	@set -e; \
	@echo "Uninstalling MinIO Tenant..."
	helm uninstall --namespace $(NAMESPACE) \
		minio-tenant
	@echo "MinIO Tenant uninstallation complete!"

generate-self-signed-cert:
	@set -e; \
	@echo "Generating self-signed certificate for MinIO..."
	openssl req -new -x509 -nodes -days 730 -keyout infra/certs/minio/selfsigned.key \
		-out infra/certs/minio/selfsigned.crt \
		-config infra/certs/minio/openssl.conf
	@echo "Self-signed certificate generated at infra/certs/minio/selfsigned.crt"

register-self-signed-cert:
	@set -e; \
	@echo "Registering self-signed certificate with Kubernetes..."
	kubectl delete secret minio-selfsigned-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret tls minio-selfsigned-secret \
		--key infra/certs/minio/selfsigned.key \
		--cert infra/certs/minio/selfsigned.crt \
		--namespace $(NAMESPACE); \
	kubectl delete secret operator-ca-tls --namespace $(NAMESPACE) || true; \
	kubectl create secret generic operator-ca-tls \
   		--from-file=public.crt=infra/certs/minio/selfsigned.crt \
		--from-file=private.key=infra/certs/minio/selfsigned.key \
		--namespace $(NAMESPACE)

create-nodeport:
	@set -e; \
	kubectl apply -f infra/services/minio/console-nodeport.yaml
	@echo "MinIO Console NodePort service created."

delete-nodeport:
	@set -e; \
	kubectl delete -f infra/services/minio/console-nodeport.yaml || true
	@echo "MinIO Console NodePort service deleted."

help:
	@echo "Makefile commands:"
	@echo "make install			       		- Install MinIO Operator and Tenant"
	@echo "make uninstall     				- Uninstall MinIO Operator and Tenant"
	@echo "make install-operator    		- Install MinIO Operator"
	@echo "make install-tenant      		- Install MinIO Tenant"
	@echo "make uninstall-operator  		- Uninstall MinIO Operator"
	@echo "make uninstall-tenant    		- Uninstall MinIO Tenant"
	@echo "make generate-self-signed-cert 	- Generate a self-signed certificate"
	@echo "make register-self-signed-cert 	- Register the self-signed certificate with Kubernetes"
	@echo "make create-nodeport             - Expose MinIO Console via NodePort (9443 -> 30943)"
	@echo "make delete-nodeport             - Delete MinIO NodePort services (Console)"
