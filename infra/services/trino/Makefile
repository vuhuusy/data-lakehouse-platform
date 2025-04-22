# Makefile for Trino deployment

NAMESPACE ?= trino
TRINO_OPERATOR ?= trino/trino

.DEFAULT_GOAL := help

.PHONY: \
	help \
	build-trino-custom-dockerfile \
	install \
	uninstall \
	release-docker-images \
	create-ui-nodeport

help:
	@echo ""
	@echo "Trino Makefile commands:"
	@echo "  make build-trino-custom-dockerfile   Build custom Trino Docker image (tag: huusy/trino:470)"
	@echo "  make release-docker-images           Push custom Docker image to registry"
	@echo "  make install                         Deploy Trino via Helm and expose UI via NodePort"
	@echo "  make uninstall                       Uninstall Trino and remove NodePort service"
	@echo "  make create-ui-nodeport              Create NodePort service for Trino Web UI (port 30080)"
	@echo "  make help                            Show this help message"
	@echo ""

build-trino-custom-dockerfile:
	@set -ex; \
	docker build \
		-t huusy/trino:470 \
		-f infra/services/trino/Dockerfile .

release-docker-images:
	@set -ex; \
	docker push huusy/trino:470

install:
	@set -ex; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \
	helm upgrade --install --namespace $(NAMESPACE) \
		trino $(TRINO_OPERATOR) \
		-f infra/services/trino/values.yaml; \

install-catalog:
	@set -ex; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \
	helm upgrade --install --namespace $(NAMESPACE) \
		trino $(TRINO_OPERATOR) \
		-f infra/services/trino/catalogs.yaml; \

create-ui-nodeport:
	@set -ex; \
	kubectl apply -n $(NAMESPACE) -f infra/services/trino/trino-ui-nodeport.yaml || true; \

uninstall:
	@set -ex; \
	helm uninstall --namespace $(NAMESPACE) trino || true; \
	kubectl delete service trino-ui-nodeport -n $(NAMESPACE) --ignore-not-found
