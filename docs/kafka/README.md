## Kafka

make -f infra/services/kafka/Makefile create-namespace
make -f infra/services/kafka/Makefile generate-self-signed-cert-keystore-truststore
make -f infra/services/kafka/Makefile register-self-signed-cert-keystore-truststore
make -f infra/services/kafka/Makefile install-kafka
make -f infra/services/kafka/Makefile create-kafka-client-pod

PRODUCER:
        kafka-console-producer.sh \
            --producer.config /tmp/client.properties \
            --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
            --topic test

CONSUMER:
        kafka-console-consumer.sh \
            --consumer.config /tmp/client.properties \
            --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
            --topic test \
            --from-beginning

LIST:
        kafka-topics.sh \
            --command-config /tmp/client.properties \
            --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
            --list



## Kafka Connect

make -f infra/services/kafka/kafka-connect/Makefile build-custom-dockerfile CONNECT_HOST=103.179.172.171:30083

make -f infra/services/kafka/kafka-connect/Makefile release-docker-image CONNECT_HOST=103.179.172.171:30083

make -f infra/services/kafka/kafka-connect/Makefile install CONNECT_HOST=103.179.172.171:30083