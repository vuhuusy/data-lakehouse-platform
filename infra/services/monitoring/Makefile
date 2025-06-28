.DEFAULT_GOAL := help

NAMESPACE ?= monitoring
CHART ?= prometheus-community/kube-prometheus-stack

.PHONY: \
	create-namespace \
	install \
	uninstall \
	help

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install: create-namespace
	@set -e; \
	printf '\033[1;33mInstalling Prometheus Stack...\033[0m\n'; \
	helm repo list | grep -q prometheus-community || helm repo add prometheus-community https://prometheus-community.github.io/helm-charts; \
	helm repo update; \
	helm upgrade --install kube-prometheus-stack $(CHART) \
		--namespace $(NAMESPACE) \
		-f infra/services/monitoring/values.yaml; \
	printf '\033[1;32mPrometheus Stack installation complete.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling Prometheus Stack...\033[0m\n'; \
	helm uninstall kube-prometheus-stack --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mPrometheus Stack uninstalled.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install            - Install Prometheus Stack into '$(NAMESPACE)' namespace"
	@echo "  make uninstall          - Uninstall Prometheus Stack"
	@echo "  make create-namespace   - Create the monitoring namespace (if not exists)"
