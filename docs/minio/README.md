# Deploy MinIO On Kubernetes

This guide walks you through installing MinIO using Helm and setting up the MinIO Client (mc) on Linux.


## Prerequisites

Before starting, ensure that the following tools are installed:
- Kubernetes cluster up and running
- kubectl for interacting with the cluster
- Helm for managing Kubernetes applications
- Make (GNU Make) for automating build and deployment tasks
- OpenSSL installed on your machine for generating certificates

Ensure you are in the root directory of the project before running these commands


## Create Kubernetes Namespace for MinIO

```bash
kubectl create namespace minio & kubectl config set-context --current --namespace=minio
```


## Create Self-Signed Certificates

To ensure secure communication between clients and the MinIO storage service, it is essential to configure SSL/TLS encryption.

> Note: While self-signed certificates are suitable for development and testing environments, a trusted CA-issued certificate is recommended for production deployments.

```bash
# Generate self-signed certificate
make -f infra/services/minio/Makefile generate-self-signed-cert

# Register self-signed certificate
make -f infra/services/minio/Makefile register-self-signed-cert
```


## Configure the MinIO Helm Repository

Add the MinIO Helm repository and update the chart list:

```bash
helm repo add minio-operator https://operator.min.io
helm repo update

# Validate the repo contents using helm search
helm search repo minio-operator

#The response should resemble the following:
NAME                            CHART VERSION   APP VERSION     DESCRIPTION                    
minio-operator/minio-operator   4.3.7           v4.3.7          A Helm chart for MinIO Operator
minio-operator/operator         7.0.0           v7.0.0          A Helm chart for MinIO Operator
minio-operator/tenant           7.0.0           v7.0.0          A Helm chart for MinIO Operator
```


## Download MinIO Operator and Tenant values.yaml file

```bash
curl -sLo infra/services/minio/operator/values.yaml https://raw.githubusercontent.com/minio/operator/master/helm/operator/values.yaml

curl -sLo infra/services/minio/tenant/values.yaml https://raw.githubusercontent.com/minio/operator/master/helm/tenant/values.yaml
```

Ensure that ``externalCertSecret`` is configured to reference your custom TLS secret and that ``requestAutoCert`` is set to false, so the server uses your self-signed certificate instead of generating one automatically.

```bash
# MinIO Tenant values.yaml
externalCertSecret:
  - name: minio-selfsigned-secret
    type: kubernetes.io/tls

requestAutoCert: false
```

## Install MinIO Operator and Tenant

```bash
make -f infra/services/minio/Makefile install-minio

# Verify the Operator installation
kubectl get all -n minio

# The response should resemble the following:
NAME                                 READY   STATUS    RESTARTS     AGE
pod/minio-operator-7678c5785-nn4nt   1/1     Running   0            7h4m
pod/minio-operator-7678c5785-rhpbz   1/1     Running   0            7h4m
pod/myminio-pool-0-0                 2/2     Running   0            121m
pod/myminio-pool-0-1                 2/2     Running   0            121m
pod/myminio-pool-0-2                 2/2     Running   0            121m

NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
service/minio             ClusterIP   10.43.207.86   <none>        443/TCP          7h4m
service/myminio-console   ClusterIP   10.43.108.63   <none>        9443/TCP         7h4m
service/myminio-hl        ClusterIP   None           <none>        9000/TCP         7h4m
service/operator          ClusterIP   10.43.117.16   <none>        4221/TCP         7h4m
service/sts               ClusterIP   10.43.59.76    <none>        4223/TCP         7h4m

NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/minio-operator   2/2     2            2           7h4m

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/minio-operator-7678c5785   2         2         2       7h4m

NAME                              READY   AGE
statefulset.apps/myminio-pool-0   3/3     7h4m
```

## Accessing MinIO Services via Port Forwarding

To interact with MinIO services securely from your local machine, use port forwarding to expose the necessary service ports. The following commands allow access to both the MinIO API and the MinIO web console.

```bash
# Forward MinIO API service to port 9000
kubectl port-forward service/myminio-hl 9000 -n minio &

# Forward MinIO Console service to port 9443
kubectl port-forward service/myminio-console 9443 -n minio &
```

After running the commands, you can:
- Access MinIO API at `https://localhost:9000` using MinIO client (mc) or S3-compatible tools.
- Access MinIO Console at `https://localhost:9443` via a web browser.


## Install the mc command line tool

```bash
curl https://dl.min.io/client/mc/release/linux-amd64/mc \
  --create-dirs \
  -o $HOME/minio-binaries/mc

chmod +x $HOME/minio-binaries/mc
echo 'export PATH=$PATH:$HOME/minio-binaries/' >> ~/.bashrc
source ~/.bashrc

# Verify the installation by running
mc --help
```

For installation instructions on Windows, macOS, and other platforms, please refer to the [<u>official documentation</u>](https://min.io/docs/minio/linux/reference/minio-mc.html#install-mc)


## Configuring MinIO Client

### Set Up MinIO Client Alias

Once MinIO is accessible via port forwarding, use the MinIO Client (mc) to configure an alias and create storage buckets.

The following command configures an alias for MinIO, enabling interaction via mc:

```bash
mc alias set myminio https://localhost:9000 minio minio123 --insecure
```

`--insecure` → Allows connection to MinIO without verifying SSL certificates (useful for self-signed certificates).

> Note: In production, use valid SSL certificates and remove --insecure.

### Create Buckets

Create storage buckets for data organization:

```bash
# Create a generic bucket
mc mb myminio/bronze-zone --insecure

# Create a dedicated Nessie warehouse bucket
mc mb myminio/nessie-warehouse --insecure
```
