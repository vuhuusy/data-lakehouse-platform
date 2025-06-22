# Scalable Real-time Fraud Detection Engine Built on Lakehouse Architecture

# Table of Contents
- [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Data Lakehouse Architecture](#data-lakehouse-architecture)
  - [Quick Start](#quick-start)
    - [Install Ansible](#install-ansible)
    - [Create RKE2 cluster](#create-rke2-cluster)
    - [Install longhorn](#install-longhorn)
    - [Install Minio](#install-minio)
    - [Install Spark](#install-spark)
    - [Install Airflow](#install-airflow)
    - [Install Hive Metastore](#install-hive-metastore)
    - [Install Kafka](#install-kafka)
    - [Install sources](#install-sources)
    - [Install Kafka Connect](#install-kafka-connect)
    - [Install Trino](#install-trino)
    - [Install Datahub](#install-datahub)
  - [License](#license)

## Overview

## Data Lakehouse Architecture

![Data Lakehouse Architecture](figures/architecture.png)

## Quick Start

### Install Ansible

```bash
apt update
apt install -y software-properties-common
add-apt-repository -y --update ppa:ansible/ansible
apt install -y ansible
```

Then in the root of this repo, run:

```bash
ansible-playbook infra/ansible/playbooks/base-setup.yml
ansible-playbook infra/ansible/playbooks/setup-rancher-nodes.yml
```

Run Rancher on Docker:

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

### Create RKE2 cluster

In Rancher UI home page, click ``Create``then choose ``Custom``for a self-hosted K8s cluster.

Pick a name for your cluster (e.g. lakehouse) and left other options as default.

![image](https://github.com/user-attachments/assets/d417b3fd-5061-46ca-b823-63c99cd94595)


In ``Registration`` step, choose ``etcd`` and ``Control Plane`` roles to be seted up onto your master node(s).

After that, the ``Worker`` role will be seted up onto your worker node(s).

Note: Select the ``Insecure`` option to skip TLS verification.

### Nodes Registration

Change the server_url, token, and ca_checksum to fit with your cluster.

```bash
nano infra/ansible/inventory/group_vars/all.yml
```

Then run ansible-playbook:

```bash
ansible-playbook infra/ansible/playbooks/setup-rke2-nodes.yml
```

### Set alias for kubectl shortcuts

```bash
nano ~/.bashrc
```

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kdp='kubectl describe pod'
alias kgn='kubectl get nodes'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
# add more for your needs, then apply the change
```

```bash
source ~/.bashrc
```

### Install longhorn

First, in your RKE cluster, get the KUBECONFIG from top left of the Rancher UI. Copy that and put into your Rancher host.

![image](https://github.com/user-attachments/assets/d54e1ff7-23e8-4f60-9397-62f9b731485f)


```bash
mkdir -p ~/.kube
nano ~/.kube/config
# Paste your KUBECONFIG into that file
```

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update

make longhorn-install
```

### Install Minio

[Link to Minio Docs]

### Install Spark

### Install Airflow

### Install Hive Metastore

### Install Kafka

### Install sources

### Install Kafka Connect

### Install Trino

### Install Datahub

## License
