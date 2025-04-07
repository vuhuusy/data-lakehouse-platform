.DEFAULT_GOAL := help

# Variables
NAMESPACE ?= lakehouse
AIRFLOW_OPERATOR ?= apache-airflow/airflow

# Define phony targets
.PHONY: install-airflow uninstall-airflow \
		help

# Install Airflow
install-airflow:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values infra/services/airflow/values.yaml \
		airflow $(AIRFLOW_OPERATOR)

# Uninstall Airflow
uninstall-airflow:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		airflow


# Show help message
help:
	@echo "Makefile commands:"
	@echo "  install-airflow: Install Airflow"
	@echo "  uninstall-airflow: Uninstall Airflow"
	@echo "  help: Show this message"