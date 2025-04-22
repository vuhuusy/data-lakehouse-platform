# Makefile for Trino deployment

NAMESPACE ?= trino
TRINO_OPERATOR ?= trino/trino

# Optional targets for specific components
.PHONY: build-trino-custom-dockerfile install uninstall

build-trino-custom-dockerfile:
	@set -ex; \
	docker build \
		-t huusy/trino:470 \
		-f infra/services/trino/Dockerfile .

install:
	@set -ex; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \
	helm upgrade --install --namespace $(NAMESPACE) \
		trino $(TRINO_OPERATOR) \
		  -f infra/services/trino/values.yaml

uninstall:
	@set -ex; \
	helm uninstall --namespace $(NAMESPACE) \
		trino

release-docker-images:
	@set -ex; \
	docker push huusy/trino:470
