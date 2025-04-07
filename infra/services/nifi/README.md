# **Deploy NiFi Cluster on Kubernetes using Helm**

This guide walks you through installing a NiFi Cluster on Kubernetes using Helm.


## **Prerequisites**

Before starting, ensure that the following tools are installed:

- **Kubernetes cluster** up and running
- **kubectl** for interacting with the cluster
- **Helm** for managing Kubernetes applications
- **Make (GNU Make)** for automating build and deployment tasks
- **MinIO** installed with **Self-Signed Certificates** for secure communication

Ensure you are in the **root directory** of the project before running these commands.


## Configure the NiFi Helm Repository

Add the NiFi Helm repository and update the chart list:

```bash
helm repo add cetic https://cetic.github.io/helm-charts
helm repo update

# Validate the repo contents using helm search
helm search repo cetic

#The response should resemble the following:
NAME                    CHART VERSION   APP VERSION     DESCRIPTION                                       
cetic/adminer           0.2.1           4.8.1           Adminer is a full-featured database management ...
cetic/drupal            0.1.0           1.16.0          Drupal is a free and open-source web content ma...
cetic/fadi              0.3.1           0.3.1           FADI is a Cloud Native platform for Big Data ba...
cetic/job               0.1.1           0.1.1           A Helm chart which provide a DRY job deployment...
cetic/microservice      0.6.0           0.6.0           A Helm chart which provide a DRY microservice d...
cetic/mlflow            1.5.1           1.5.1           A Helm chart for MLFlow                           
cetic/nifi              1.2.1           1.23.2          Apache NiFi is a software project from the Apac...
cetic/pgadmin           0.1.12          4.13.0          pgAdmin is a web based administration tool for ...
cetic/phpldapadmin      0.1.4           0.7.1           Web-based LDAP browser to manage your LDAP server 
cetic/postgresql        0.2.5           11.5.0          PostgreSQL is an open-source object-relational ...
cetic/static            0.1.1           0.1.1           A Helm chart to deploy k8s static files           
cetic/swaggerui         0.3.6           3.24.3          Swagger is an open-source software framework ba...
cetic/thingsboard       0.1.2           2.2             A Helm chart for Kubernetes                       
cetic/tsaas             0.1.5           0.1.8           A Helm chart for Tsimulus as a Service            
cetic/tsorage           0.4.11          1.0.0           A platform for collecting, storing, and process...
cetic/zabbix            3.1.3           6.0.8           Zabbix is a mature and effortless enterprise-cl...
```


## Download NiFi values.yaml file

```bash
curl -sLo infra/services/nifi/values.yaml https://raw.githubusercontent.com/cetic/helm-nifi/master/values.yaml
```
Change this in values.yaml file:
- replicaCount: 3 (to setup a 3 node cluster)
- enable certManager
- repository: huusy/nifi to use custom Docker image
- isNode: true

To set up certManager, please refer to [this](https://medium.com/@TheNileshkumar/setup-apache-nifi-cluster-in-kubernates-fce5dca0bdbc)


## Install Cert Manager

First, we will have to install certManager to enable certManager properties from the previous step. 

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Validate the repo contents using helm search
helm search repo jetstack

#The response should resemble the following:
NAME                                    CHART VERSION   APP VERSION     DESCRIPTION                                       
jetstack/cert-manager                   v1.17.1         v1.17.1         A Helm chart for cert-manager                     
jetstack/cert-manager-approver-policy   v0.19.0         v0.19.0         approver-policy is a CertificateRequest approve...
jetstack/cert-manager-csi-driver        v0.10.2         v0.10.2         cert-manager csi-driver enables issuing secretl...
jetstack/cert-manager-csi-driver-spiffe v0.8.2          v0.8.2          csi-driver-spiffe is a Kubernetes CSI plugin wh...
jetstack/cert-manager-google-cas-issuer v0.9.0          v0.9.0          A Helm chart for jetstack/google-cas-issuer       
jetstack/cert-manager-istio-csr         v0.14.0         v0.14.0         istio-csr enables the use of cert-manager for i...
jetstack/cert-manager-trust             v0.2.1          v0.2.0          DEPRECATED: The old name for trust-manager. Use...
jetstack/finops-dashboards              v0.0.5          0.0.5           A Helm chart for Kubernetes                       
jetstack/finops-policies                v0.0.6          v0.0.6          A Helm chart for Kubernetes                       
jetstack/finops-stack                   v0.0.5          0.0.3           A FinOps Stack for Kubernetes                     
jetstack/trust-manager                  v0.16.0         v0.16.0         trust-manager is the easiest way to manage TLS ...
jetstack/version-checker                v0.8.6          v0.8.6          A Helm chart for version-checker       

# Install Cert Manager
make -f infra/services/nifi/Makefile install-cert-manager
```


## Install NiFi

After installing Cert Manager, we are ready to install NiFi.

```bash
make -f infra/services/nifi/Makefile install-nifi
```


## Accessing NiFi UI via Port Forwarding

```bash
# Forward NiFi service to port 8443
kubectl port-forward service/nifi 8443 -n lakehouse &
```

After running the commands, you can ccess NiFi UI at `https://localhost:8443/nifi/` via a web browser.


<!-- Endpoint Override URL:
https://minio.lakehouse.svc.cluster.local:443 -->