.DEFAULT_GOAL := help

NAMESPACE ?= feature-store
CHART ?= bitnami/redis
IMAGE_TAG ?= huusy/feast:0.16.1

.PHONY: \
	install-online-store \
	uninstall-online-store \
	create-namespace \
	build-image \
	release-image \
	help

install-online-store: create-namespace
	@set -e; \
	printf '\033[1;33mInstalling Redis as Feast Online Store...\033[0m\n'; \
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami; \
	helm repo update; \
	helm upgrade --install redis $(CHART) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/feast/online-store/values.yaml; \
	printf '\033[1;32mFeast Online Store installed.\033[0m\n'

uninstall-online-store:
	@set -e; \
	printf '\033[1;33mUninstalling Feast Online Store (Redis)...\033[0m\n'; \
	helm uninstall redis --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mUninstalled.\033[0m\n'

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

build-image:
	@set -e; \
	printf '\033[1;33mBuilding Feast Online Store Docker image...\033[0m\n'; \
	docker build -t $(IMAGE_TAG) -f infra/services/feast/Dockerfile .; \
	printf '\033[1;32mImage built: $(IMAGE_TAG)\033[0m\n'

release-image:
	@set -e; \
	printf '\033[1;33mPushing Feast Online Store Docker image...\033[0m\n'; \
	docker push $(IMAGE_TAG); \
	printf '\033[1;32mImage pushed: $(IMAGE_TAG)\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install-online-store      - Install Redis as Feast Online Store into '$(NAMESPACE)'"
	@echo "  make uninstall-online-store    - Uninstall Redis from '$(NAMESPACE)'"
	@echo "  make create-namespace          - Create namespace $(NAMESPACE) if not exists"
	@echo "  make build-image               - Build Feast Online Store Dock
