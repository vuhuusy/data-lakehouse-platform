NAMESPACE ?= monitoring
CHART ?= prometheus-community/kube-prometheus-stack

.PHONY: \
	create-namespace \
	install \
	uninstall

create-namespace:
	@set -e; \
	kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install: create-namespace
	@set -e; \
	helm upgrade --install kube-prometheus-stack $(CHART) -n $(NAMESPACE) \
		-f infra/services/monitoring/values.yaml

uninstall:
	@set -e; \
	helm uninstall kube-prometheus-stack -n $(NAMESPACE) || true