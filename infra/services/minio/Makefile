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
	printf '\033[1;33mInstalling MinIO Operator...\033[0m\n'; \
	helm repo list | grep -q minio-operator || helm repo add minio-operator https://operator.min.io; \
	helm repo update; \
	helm upgrade --install minio-operator $(MINIO_OPERATOR) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/minio/operator/values.yaml; \
	printf '\033[1;32mMinIO Operator installation complete.\033[0m\n'

install-tenant:
	@set -e; \
	printf '\033[1;33mInstalling MinIO Tenant...\033[0m\n'; \
	helm upgrade --install minio-tenant $(MINIO_TENANT) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/minio/tenant/values.yaml; \
	printf '\033[1;32mMinIO Tenant installation complete.\033[0m\n'

uninstall-operator:
	@set -e; \
	printf '\033[1;33mUninstalling MinIO Operator...\033[0m\n'; \
	kubectl delete secret minio-selfsigned-secret --namespace $(NAMESPACE) || true; \
	helm uninstall --namespace $(NAMESPACE) minio-operator; \
	printf '\033[1;32mMinIO Operator uninstalled.\033[0m\n'

uninstall-tenant:
	@set -e; \
	printf '\033[1;33mUninstalling MinIO Tenant...\033[0m\n'; \
	helm uninstall --namespace $(NAMESPACE) minio-tenant; \
	printf '\033[1;32mMinIO Tenant uninstalled.\033[0m\n'

generate-self-signed-cert:
	@set -e; \
	printf '\033[1;33mGenerating self-signed certificate...\033[0m\n'; \
	openssl req -new -x509 -nodes -days 730 -keyout infra/certs/minio/selfsigned.key \
		-out infra/certs/minio/selfsigned.crt \
		-config infra/certs/minio/openssl.conf; \
	printf '\033[1;32mCertificate generated at infra/certs/minio/selfsigned.crt\033[0m\n'

register-self-signed-cert:
	@set -e; \
	printf '\033[1;33mRegistering self-signed certificate...\033[0m\n'; \
	kubectl delete secret minio-selfsigned-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret tls minio-selfsigned-secret \
		--key infra/certs/minio/selfsigned.key \
		--cert infra/certs/minio/selfsigned.crt \
		--namespace $(NAMESPACE); \
	kubectl delete secret operator-ca-tls --namespace $(NAMESPACE) || true; \
	kubectl create secret generic operator-ca-tls \
		--from-file=public.crt=infra/certs/minio/selfsigned.crt \
		--from-file=private.key=infra/certs/minio/selfsigned.key \
		--namespace $(NAMESPACE); \
	printf '\033[1;32mSelf-signed certificate registered.\033[0m\n'

create-nodeport:
	@set -e; \
	printf '\033[1;33mCreating MinIO Console NodePort...\033[0m\n'; \
	kubectl apply -f infra/services/minio/console-nodeport.yaml; \
	printf '\033[1;32mNodePort service created.\033[0m\n'

delete-nodeport:
	@set -e; \
	printf '\033[1;33mDeleting MinIO Console NodePort...\033[0m\n'; \
	kubectl delete -f infra/services/minio/console-nodeport.yaml || true; \
	printf '\033[1;32mNodePort service deleted.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                     - Install MinIO Operator and Tenant"
	@echo "  make uninstall                  - Uninstall MinIO Operator and Tenant"
	@echo "  make install-operator           - Install MinIO Operator"
	@echo "  make install-tenant             - Install MinIO Tenant"
	@echo "  make uninstall-operator         - Uninstall MinIO Operator"
	@echo "  make uninstall-tenant           - Uninstall MinIO Tenant"
	@echo "  make generate-self-signed-cert  - Generate a self-signed certificate"
	@echo "  make register-self-signed-cert  - Register the self-signed certificate with Kubernetes"
	@echo "  make create-nodeport            - Expose MinIO Console via NodePort (9443 -> 30943)"
	@echo "  make delete-nodeport            - Delete MinIO NodePort services (Console)"
