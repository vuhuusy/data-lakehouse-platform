# Data Lakehouse Platform - A Modern Architecture

# Table of Contents
- [Data Lakehouse Platform - A Modern Architecture](#data-lakehouse-platform---a-modern-architecture)
- [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Data Lakehouse Architecture](#data-lakehouse-architecture)
  - [Getting Started](#getting-started)
  - [License](#license)

## Overview

## Data Lakehouse Architecture

## Quick Start

### Install Ansible on Rancher machine

```bash
apt update
apt install -y software-properties-common
add-apt-repository -y --update ppa:ansible/ansible
apt install -y ansible
```

Then in the root of this repo, run:

```bash
ansible-playbook infra/ansible/playbooks/base-setup.yml
ansible-playbook infra/ansible/playbooks/setup_rancher.yml
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

### Create a Rancher Kubernetes Engine (RKE2) cluster

In Rancher UI home page, click ``Create``then choose ``Custom``for a self-hosted K8s cluster.

Pick a name for your cluster (e.g. lakehouse) and left other options as default.

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
ansible-playbook infra/ansible/playbooks/setup_rke2_nodes.yml
```

### Set alias for kubectl shortcuts

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
# add more for your needs, then apply the change

source ~/.bashrc
```

### Install longhorn

First, in your RKE cluster, get the KUBECONFIG from top left of the Rancher UI. Copy that and put into your Rancher host.

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
