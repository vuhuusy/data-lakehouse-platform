k apply -f script/spark-stream-jobs/customer/kafka_to_delta_customer.yaml -n spark-operator
k apply -f script/spark-stream-jobs/merchant/kafka_to_delta_merchant.yaml -n spark-operator
k apply -f script/spark-stream-jobs/transaction/kafka_to_delta_transaction.yaml -n spark-operator
k apply -f script/spark-stream-jobs/predicted-transaction/predicted-transaction.yaml -n spark-operator

k apply -f script/flink-jobs/flink-kafka-job.yaml -n flink

<!-- k apply -f script/spark-stream-jobs/customer/nodeport.yaml -n spark-operator
k apply -f script/spark-stream-jobs/merchant/nodeport.yaml -n spark-operator
k apply -f script/spark-stream-jobs/transaction/nodeport.yaml -n spark-operator -->

k delete -f script/spark-stream-jobs/customer/kafka_to_delta_customer.yaml -n spark-operator
k delete -f script/spark-stream-jobs/merchant/kafka_to_delta_merchant.yaml -n spark-operator
k delete -f script/spark-stream-jobs/transaction/kafka_to_delta_transaction.yaml -n spark-operator
k delete -f script/spark-stream-jobs/predicted-transaction/predicted-transaction.yaml -n spark-operator

k delete -f script/flink-jobs/flink-kafka-job.yaml -n flink

<!-- k delete -f script/spark-stream-jobs/customer/nodeport.yaml -n spark-operator
k delete -f script/spark-stream-jobs/merchant/nodeport.yaml -n spark-operator
k delete -f script/spark-stream-jobs/transaction/nodeport.yaml -n spark-operator -->