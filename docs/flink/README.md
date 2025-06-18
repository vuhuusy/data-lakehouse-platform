```bash
kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v1.8.2/cert-manager.yaml

helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.11.0/

helm install flink-operator flink-operator-repo/flink-kubernetes-operator -n flink

kubectl create -f https://raw.githubusercontent.com/apache/flink-kubernetes-operator/release-1.11/examples/basic.yaml -n flink
```

```bash
nano flink-nodeport.yaml

apiVersion: v1
kind: Service
metadata:
  name: flink-ui
  namespace: flink
spec:
  type: NodePort
  selector:
    app: basic-example
  ports:
    - protocol: TCP
      port: 8081
      targetPort: 8081
      nodePort: 30000
	  
k apply -f flink-nodeport.yaml

k delete -f flink-nodeport.yaml -n flink
```