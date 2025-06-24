NAMESPACE ?= superset
CHART_SUPERSET ?= superset/superset

.PHONY: install uninstall \
		build-superset-custom-dockerfile \
		release-docker-images

install: create-namespace install-superset

uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) superset || true

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-superset:
	@set -e; \
	helm list | grep -q superset || helm repo add superset https://apache.github.io/superset

	helm upgrade --install --namespace $(NAMESPACE) \
		superset $(CHART_SUPERSET) \
		-f infra/services/superset/values.yaml

build-superset-custom-dockerfile:
	@set -e; \
	docker build -t huusy/superset:3.0.0 \
	 -f infra/services/superset/Dockerfile .

release-docker-images:
	@set -e; \
	docker push huusy/superset:3.0.0