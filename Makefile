.PHONY: longhorn-install

longhorn-install:
	helm upgrade --install longhorn longhorn/longhorn \
	  --namespace longhorn-system \
	  --create-namespace \
	  --set defaultSettings.defaultDataPath="/var/lib/longhorn/" \
	  --set persistence.defaultClass=true

	kubectl apply -f infra/services/longhorn/storageclasses.yaml