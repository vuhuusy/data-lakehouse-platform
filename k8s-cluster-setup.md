# On master node:

nano /etc/hosts

# K8s Nodes
10.128.0.6 k8s-worker-1
10.128.0.2 k8s-worker-2


# On worker node:

add others ip host mapping node


# K8s Nodes
10.128.0.6 k8s-master
10.128.0.2 k8s-worker-2

# K8s Nodes
10.128.0.6 k8s-master
10.128.0.2 k8s-worker-1

Disable swap

sudo nano /etc/fstab

Comment it out by adding # at the beginning:

#UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx none swap sw 0 0

swapon --show

sudo rm /swapfile


curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg



sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null


sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

kubeadm join 10.128.0.5:6443 --token 4ckybf.832b28esid9m95d3 \
        --discovery-token-ca-cert-hash sha256:58659af27e300d7e80d9aebc66e391fe2815bdb6ddf8d200041697c87955e338 


kubectl label node k8s-worker-1 node-role.kubernetes.io/worker=worker
kubectl label node k8s-worker-2 node-role.kubernetes.io/worker=worker


curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

chmod 700 get_helm.sh

./get_helm.sh