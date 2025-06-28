.PHONY: install

install:
	@set -e; \
	printf '\033[1;33mInstalling Longhorn...\033[0m\n'; \
	helm repo list | grep -q longhorn || helm repo add longhorn https://charts.longhorn.io; \
	helm repo update; \
	helm upgrade --install longhorn longhorn/longhorn \
	  --namespace longhorn \
	  --create-namespace \
	  -f infra/services/longhorn/values.yaml; \
	kubectl apply -f infra/services/longhorn/custom-storageclasses.yaml; \
	printf '\033[1;32mLonghorn installation complete!\033[0m\n'
