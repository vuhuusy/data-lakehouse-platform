.DEFAULT_GOAL := help

NAMESPACE ?= trino
TRINO_OPERATOR ?= trino/trino

.PHONY: \
	install uninstall \
	build-trino-custom-dockerfile \
	release-docker-images \
	create-namespace \
	create-coordinator-nodeport \
	install-trino \
	help

install: create-namespace install-trino create-coordinator-nodeport

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-trino:
	@set -e; \
	printf '\033[1;33mInstalling Trino...\033[0m\n'; \
	helm repo list | grep -q trino || helm repo add trino https://trinodb.github.io/charts; \
	helm repo update; \
	helm upgrade --install trino $(TRINO_OPERATOR) \
		--namespace $(NAMESPACE) \
		-f infra/services/trino/values.yaml; \
	printf '\033[1;32mTrino installed.\033[0m\n'

create-coordinator-nodeport:
	@set -e; \
	printf '\033[1;33mCreating NodePort service for Trino Web UI...\033[0m\n'; \
	kubectl apply -n $(NAMESPACE) -f infra/services/trino/coordinator-nodeport.yaml; \
	printf '\033[1;32mNodePort service created.\033[0m\n'

build-trino-custom-dockerfile:
	@set -e; \
	printf '\033[1;33mBuilding Trino Docker image...\033[0m\n'; \
	docker build \
		-t huusy/trino:470 \
		-f infra/services/trino/Dockerfile .; \
	printf '\033[1;32mImage built.\033[0m\n'

release-docker-images:
	@set -e; \
	printf '\033[1;33mPushing Trino Docker image...\033[0m\n'; \
	docker push huusy/trino:470; \
	printf '\033[1;32mImage pushed.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling Trino...\033[0m\n'; \
	helm uninstall trino --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mTrino uninstalled.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make build-trino-custom-dockerfile   - Build custom Trino Docker image (huusy/trino:470)"
	@echo "  make release-docker-images           - Push Docker image to registry"
	@echo "  make install                         - Install Trino and expose Web UI"
	@echo "  make uninstall                       - Uninstall Trino and clean up"
	@echo "  make create-coordinator-nodeport     - Expose Trino coordinator Web UI via NodePort"
	@echo "  make help                            - Show this help message"
