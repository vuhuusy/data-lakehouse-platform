import json
import requests
import os
from pyflink.datastream import StreamExecutionEnvironment, RuntimeContext, KeyedProcessFunction
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
if not SLACK_TOKEN:
    raise ValueError("SLACK_TOKEN environment variable not set")

SLACK_URL = "https://slack.com/api/chat.postMessage"
SLACK_CHANNEL = "frauddetectionalert"
HEADERS = {
    "Authorization": f"Bearer {SLACK_TOKEN}",
    "Content-type": "application/json; charset=utf-8"
}

class SlackAlertFunction(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        pass

    def process_element(self, value, ctx):
        try:
            data = json.loads(value)
            if data.get("is_fraud") == 1:
                msg = (
                    f"*Fraud Alert!*\n"
                    f"*Time:* {data.get('date')} {data.get('time')}\n"
                    f"*Amount:* ${data.get('amt')}\n"
                    f"*Customer:* `{data.get('customer_id')}`\n"
                    f"*Merchant:* `{data.get('merchant_id')}`"
                )
                payload = {
                    "channel": SLACK_CHANNEL,
                    "text": msg
                }
                resp = requests.post(SLACK_URL, headers=HEADERS, json=payload)
                if not resp.ok:
                    print(f"[ERROR] Slack response: {resp.text}")
        except Exception as e:
            print(f"[ERROR] {e}")

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    kafka_props = {
        'bootstrap.servers': 'kafka.kafka.svc.cluster.local:9092',
        'group.id': 'flink.fraud.slack',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'SCRAM-SHA-256',
        'sasl.jaas.config': 'org.apache.kafka.common.security.scram.ScramLoginModule required username="kafka" password="kafka";',
        'ssl.truststore.location': '/opt/flink/secrets/kafka.truststore.jks',
        'ssl.truststore.password': 'changeit',
        'ssl.keystore.location': '/opt/flink/secrets/kafka.keystore.jks',
        'ssl.keystore.password': 'changeit',
        'auto.offset.reset': 'latest'
    }

    source = FlinkKafkaConsumer(
        topics='financial-ops.alert.transaction',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    env.add_source(source) \
       .key_by(lambda x: json.loads(x).get("after", {}).get("customer_id", "")) \
       .process(SlackAlertFunction())

    env.execute("Slack Fraud Alert")

if __name__ == '__main__':
    main()
