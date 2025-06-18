.PHONY: install

install:
	@set -e; \
	@echo "Installing Longhorn..."
	helm repo list | grep -q longhorn || helm repo add longhorn https://charts.longhorn.io
	helm repo update
	
	helm upgrade --install longhorn longhorn/longhorn \
	  --namespace longhorn \
	  --create-namespace \
	  -f infra/services/longhorn/values.yaml

	kubectl apply -f infra/services/longhorn/custom-storageclasses.yaml
	@echo "Longhorn installation complete!"