# Install Java 11
sudo apt update
sudo apt install openjdk-11-jdk -y

# Install Docker
```bash
nano install_docker.sh
chmod +x install_docker.sh
./install_docker.sh
```

# Install Make

```bash
sudo apt-get install -y build-essential
```

# Run Rancher in Docker
```bash
docker run -d --restart=unless-stopped \
  --name rancher \
  -p 80:80 -p 443:443 \
    --privileged \
  --memory="3g" --cpus="1.5" \
  -v /opt/rancher-data:/var/lib/rancher \
  rancher/rancher:latest
```
Get the Rancher bootstrap password

```bash
docker logs rancher 2>&1 | grep "Bootstrap Password:"
```

Open your browser at ``https://<your_rancher_host_ip_addr>`` and set a new password to use.

# Install kubectl and Helm on Rancher's host

```bash
curl -LO https://dl.k8s.io/release/v1.31.0/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

# Set alias for kubectl shortcuts

```bash
nano ~/.bashrc

alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kdp='kubectl describe pod'
alias kgn='kubectl get nodes'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
# Add more if needed

source ~/.bashrc
```

# Create a Rancher Kubernetes Engine (RKE) cluster

In Rancher UI home page, click ``Create``then choose ``Custom``for a self-hosted K8s cluster.

Pick a name for your cluster (e.g. lakehouse) and left other options as default.

In ``Registration`` step, choose ``etcd`` and ``Control Plane`` roles to be seted up onto your master node(s).

After that, the ``Worker`` role will be seted up onto your worker node(s).

Note: Select the ``Insecure`` option to skip TLS verification.

# Install longhorn

First, in your RKE cluster, get the KUBECONFIG from top left of the Rancher UI. Copy that and put into your Rancher host.

```bash
mkdir -p ~/.kube
nano ~/.kube/config
# Paste your KUBECONFIG into that file
```

```bash
sudo mkdir -p /var/lib/longhorn
sudo chmod 777 /var/lib/longhorn

helm repo add longhorn https://charts.longhorn.io
helm repo update

kubectl create namespace longhorn-system

helm upgrade --install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --set defaultSettings.defaultDataPath="/var/lib/longhorn/" \
  --set persistence.defaultClass=true
```

Install ``nfs-common`` for Longhorn

```bash
sudo apt update
sudo apt install -y nfs-common
```

# Set the label for nodes you will use to create PV

Next, label your nodes that wil be used to create PV.

```bash
kubectl label node <your-node-name> longhorn.io/create-default-disk=true
```

After that, create 2 additional StorageClass for Retail and Delete use case.

```bash
nano longhorn-storageclasses.yaml

# Paste the content of longhorn-storageclasses.yaml file

k apply -f longhorn-storageclasses.yaml
```

Save the file and apply, then check the list of Storageclass created using

```bash
kubectl get storageclass
```

# Install Data Plaform components

kubectl create namespace minio & kubectl config set-context --current --namespace=minio





## Airflow

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
