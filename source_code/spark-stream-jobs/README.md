k apply -f source_code/spark-stream-jobs/customer/kafka_to_delta_customer.yaml -n spark-operator
k apply -f source_code/spark-stream-jobs/merchant/kafka_to_delta_merchant.yaml -n spark-operator
k apply -f source_code/spark-stream-jobs/transaction/kafka_to_delta_transaction.yaml -n spark-operator
k apply -f source_code/spark-stream-jobs/predicted-transaction/predicted-transaction.yaml -n spark-operator

<!-- k apply -f source_code/spark-stream-jobs/customer/nodeport.yaml -n spark-operator
k apply -f source_code/spark-stream-jobs/merchant/nodeport.yaml -n spark-operator
k apply -f source_code/spark-stream-jobs/transaction/nodeport.yaml -n spark-operator -->

k delete -f source_code/spark-stream-jobs/customer/kafka_to_delta_customer.yaml -n spark-operator
k delete -f source_code/spark-stream-jobs/merchant/kafka_to_delta_merchant.yaml -n spark-operator
k delete -f source_code/spark-stream-jobs/transaction/kafka_to_delta_transaction.yaml -n spark-operator
k delete -f source_code/spark-stream-jobs/predicted-transaction/predicted-transaction.yaml -n spark-operator

<!-- k delete -f source_code/spark-stream-jobs/customer/nodeport.yaml -n spark-operator
k delete -f source_code/spark-stream-jobs/merchant/nodeport.yaml -n spark-operator
k delete -f source_code/spark-stream-jobs/transaction/nodeport.yaml -n spark-operator -->