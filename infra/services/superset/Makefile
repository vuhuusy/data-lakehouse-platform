.DEFAULT_GOAL := help

NAMESPACE ?= superset
CHART_SUPERSET ?= superset/superset
IMAGE_TAG ?= huusy/superset:3.0.0

.PHONY: \
	install uninstall \
	install-superset \
	create-namespace \
	build-superset-custom-dockerfile \
	release-docker-images \
	help

install: create-namespace install-superset

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-superset:
	@set -e; \
	printf '\033[1;33mInstalling Apache Superset...\033[0m\n'; \
	helm repo list | grep -q superset || helm repo add superset https://apache.github.io/superset; \
	helm repo update; \
	helm upgrade --install superset $(CHART_SUPERSET) \
		--namespace $(NAMESPACE) \
		-f infra/services/superset/values.yaml; \
	printf '\033[1;32mSuperset installation complete.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling Superset...\033[0m\n'; \
	helm uninstall superset --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mSuperset uninstalled.\033[0m\n'

build-superset-custom-dockerfile:
	@set -e; \
	printf '\033[1;33mBuilding Superset Docker image...\033[0m\n'; \
	docker build -t $(IMAGE_TAG) \
		-f infra/services/superset/Dockerfile .; \
	printf '\033[1;32mImage built: $(IMAGE_TAG)\033[0m\n'

release-docker-images:
	@set -e; \
	printf '\033[1;33mPushing Superset Docker image...\033[0m\n'; \
	docker push $(IMAGE_TAG); \
	printf '\033[1;32mImage pushed: $(IMAGE_TAG)\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                        - Install Apache Superset via Helm"
	@echo "  make uninstall                      - Uninstall Superset"
	@echo "  make build-superset-custom-dockerfile - Build Docker image for Superset ($(IMAGE_TAG))"
	@echo "  make release-docker-images          - Push image to Docker registry"
	@echo "  make create-namespace               - Create namespace '$(NAMESPACE)'"
	@echo "  make help                           - Show this help message"
