NAMESPACE ?= feature-store

.PHONY: install-online-store uninstall-online-store

install-online-store:
	helm upgrade --install redis bitnami/redis \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/feast/online-store/values.yaml

uninstall-online-store:
	helm uninstall redis \
		--namespace $(NAMESPACE)