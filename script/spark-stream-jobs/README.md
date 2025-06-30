k apply -f script/spark-stream-jobs/customer/kafka-to-delta-customer.yaml -n spark-operator
k apply -f script/spark-stream-jobs/merchant/kafka-to-delta-merchant.yaml -n spark-operator
k apply -f script/spark-stream-jobs/transaction/kafka-to-delta-transaction.yaml -n spark-operator
k apply -f script/spark-stream-jobs/prediction-transaction/kafka-to-delta-prediction-transaction.yaml -n spark-operator

k apply -f script/flink-jobs/flink-kafka-job.yaml -n flink


k delete -f script/spark-stream-jobs/customer/kafka-to-delta-customer.yaml -n spark-operator
k delete -f script/spark-stream-jobs/merchant/kafka-to-delta-merchant.yaml -n spark-operator
k delete -f script/spark-stream-jobs/transaction/kafka-to-delta-transaction.yaml -n spark-operator
k delete -f script/spark-stream-jobs/prediction-transaction/kafka-to-delta-prediction-transaction.yaml -n spark-operator

k delete -f script/flink-jobs/flink-kafka-job.yaml -n flink


k create ns ingestion

k apply -f script/realtime-data-simulation/ingest.yaml -n ingestion