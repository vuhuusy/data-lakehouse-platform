k apply -f source_code/spark-stream-jobs/customer/kafka_to_delta_customer.yaml
k apply -f source_code/spark-stream-jobs/merchant/kafka_to_delta_merchant.yaml

k apply -f source_code/spark-stream-jobs/customer/nodeport.yaml
k apply -f source_code/spark-stream-jobs/merchant/nodeport.yaml