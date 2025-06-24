NAMESPACE ?= flink
CHART_FLINK ?= flink-operator-repo/flink-kubernetes-operator

.PHONY: install uninstall \
		create-namespace \
		build-flink-custom-dockerfile \
		release-docker-images

install: create-namespace install-flink create-secret-kafka create-flink-nodeport

uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) flink-kubernetes-operator || true; \
	kubectl delete secret kafka-jks -n $(NAMESPACE) || true; \
	kubectl delete -f infra/services/flink/flink-nodeport.yaml -n $(NAMESPACE) || true

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-cert-manager:
	@set -e; \
	kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.2/cert-manager.yaml

install-flink:
	@set -e; \
	helm repo list | grep -q flink-operator-repo || helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.12.0/

	helm upgrade --install --namespace $(NAMESPACE) \
		flink-kubernetes-operator $(CHART_FLINK) \
		-f infra/services/flink/values.yaml

build-flink-custom-dockerfile:
	@set -e; \
	docker build \
		-t huusy/flink:1.17 \
		-f infra/services/flink/Dockerfile .

release-docker-images:
	@set -e; \
	docker push huusy/flink:1.17

create-secret-kafka:
	@set -e; \
	kubectl create secret generic kafka-jks \
		--from-file=kafka.crt=infra/certs/kafka/kafka.crt \
		--from-file=kafka.key=infra/certs/kafka/kafka.key  \
		--from-file=kafka.keystore.jks=infra/certs/kafka/kafka.keystore.jks \
		--from-file=kafka.truststore.jks=infra/certs/kafka/kafka.truststore.jks \
		-n $(NAMESPACE)

create-flink-nodeport:
	@set -e; \
	kubectl apply -n $(NAMESPACE) -f infra/services/flink/flink-nodeport.yaml