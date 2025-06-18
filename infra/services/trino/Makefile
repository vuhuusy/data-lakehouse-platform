.DEFAULT_GOAL := help

NAMESPACE ?= trino
TRINO_OPERATOR ?= trino/trino

.PHONY: \
	help \
	build-trino-custom-dockerfile \
	install \
	uninstall \
	release-docker-images \
	create-namespace \
	create-coordinator-nodeport

help:
	@echo ""
	@echo "Trino Makefile commands:"
	@echo "  make build-trino-custom-dockerfile   Build custom Trino Docker image (tag: huusy/trino:470)"
	@echo "  make release-docker-images           Push custom Docker image to registry"
	@echo "  make install                         Deploy Trino via Helm and expose UI via NodePort"
	@echo "  make uninstall                       Uninstall Trino and remove NodePort service"
	@echo "  make create-coordinator-nodeport     Create NodePort service for Trino Web UI (port 30080)"
	@echo "  make help                            Show this help message"
	@echo ""

install: create-namespace install-trino create-coordinator-nodeport

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

build-trino-custom-dockerfile:
	@set -e; \
	docker build \
		-t huusy/trino:470 \
		-f infra/services/trino/Dockerfile .

release-docker-images:
	@set -e; \
	docker push huusy/trino:470

install-trino:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		trino $(TRINO_OPERATOR) \
		-f infra/services/trino/values.yaml; \

create-coordinator-nodeport:
	@set -e; \
	kubectl apply -n $(NAMESPACE) -f infra/services/trino/coordinator-nodeport.yaml

uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) trino || true