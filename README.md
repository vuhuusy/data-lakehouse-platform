# Scalable Real-time Fraud Detection Engine Built on Lakehouse Architecture

![Data Lakehouse Architecture](./figures/architecture.png)

# Table of Contents
- [Table of Contents](#table-of-contents)
- [1. Overview](#1-overview)
- [2. Quick Start](#2-quick-start)
  - [2.1. Install Ansible and Prepare Environment](#21-install-ansible-and-prepare-environment)
  - [2.2. Run Rancher with Docker](#22-run-rancher-with-docker)
  - [2.3. Create and Configure RKE2 Cluster](#23-create-and-configure-rke2-cluster)
  - [2.4. Install longhorn](#install-longhorn)
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

# 1. Overview

This project demonstrates a scalable real-time fraud detection system built on a modern Data Lakehouse architecture. It integrates batch and streaming data pipelines using open-source Big Data technologies such as Apache Flink, Kafka, Spark, Delta Lake, and MLflow. The system is designed for low-latency inference, feature enrichment, and end-to-end observability, supporting both operational analytics and machine learning in production environments.

# 2. Quick Start

## 2.1 Install Ansible and Prepare Environment

Install Ansible on your Rancher host machine (Ubuntu/Debian-based):

```bash
apt update
apt install -y software-properties-common
add-apt-repository -y --update ppa:ansible/ansible
apt install -y ansible
```

Clone this repository and navigate to the root of the project:

```bash
git clone https://github.com/vuhuusy/data-lakehouse-platform.git
cd data-lakehouse-platform
```

Run the Ansible playbooks to prepare the host:

```bash
ansible-playbook infra/ansible/playbooks/base-setup.yml
ansible-playbook infra/ansible/playbooks/setup-rancher-nodes.yml
```

## 2.2 Run Rancher with Docker

Start a standalone Rancher server using Docker:

```bash
docker run -d --restart=unless-stopped \
  --name rancher \
  -p 80:80 -p 443:443 \
    --privileged \
  --memory="3g" --cpus="1.5" \
  -v /opt/rancher-data:/var/lib/rancher \
  rancher/rancher:latest
```

Get the initial admin password (bootstrap password):

```bash
docker logs rancher 2>&1 | grep "Bootstrap Password:"
```

Access the Rancher UI in your browser:

```bash
https://<your_rancher_host_ip_addr>
```

Login with the bootstrap password and follow the instructions to set a new admin password.

## 2.3 Create and Configure RKE2 Cluster

### Create a new Kubernetes cluster in Rancher UI:
- From the Rancher home page, click Create, then choose Custom for a self-hosted K8s cluster.
- Enter a name for the cluster (e.g., lakehouse) and leave other settings as default.

![Create RKE2 cluster](https://github.com/user-attachments/assets/d417b3fd-5061-46ca-b823-63c99cd94595)


### Select node roles in the Registration step
- Assign ``etcd`` and ``Control Plane`` roles to your master node(s).
- Assign ``Worker`` role to worker node(s).
- **Important**: Select the Insecure option to disable TLS verification if needed.

### Register nodes with Ansible

Update the following variables in your inventory file:

```bash
nano infra/ansible/inventory/group_vars/all.yml
```

Edit values:

```bash
server_url: "https://<your_rancher_server_ip>"
token: "<your_cluster_token>"
ca_checksum: "<your_cluster_ca_checksum>"
```

Then run the RKE2 setup playbook:

```bash
ansible-playbook infra/ansible/playbooks/setup-rke2-nodes.yml
```

### Set up kubeconfig on your Rancher host

After the cluster is active, download its KUBECONFIG file from the top-right menu of the Rancher UI.
Copy it into your Rancher host at:

![image](https://github.com/user-attachments/assets/d54e1ff7-23e8-4f60-9397-62f9b731485f)

```bash
mkdir -p ~/.kube
nano ~/.kube/config
# Paste your KUBECONFIG into that file
```

Then verify ``kubectl`` works:

```bash
kubectl get nodes
```

### (Optional) Set useful kubectl aliases

Edit your shell config:

```bash
nano ~/.bashrc
```

Add these aliases:

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

Apply the changes:

```bash
source ~/.bashrc
```

## 2.4 Install longhorn

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update

make longhorn-install
```

## 2.5 Install Minio

[Link to Minio Docs]

## 2.6 Install Spark

## 2.7 Install Airflow

## 2.8 Install Hive Metastore

## 2.9 Install Kafka

## 2.10 Install sources

## 2.11 Install Kafka Connect

## 2.12 Install Trino

## 2.13 Install Datahub

# 3. License

MIT License. See [LICENSE](./LICENSE) for details.
