import math
import json
import pickle
import requests
from datetime import datetime
from collections import deque

from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment, KeyedProcessFunction, RuntimeContext
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.state import MapStateDescriptor

from feast import FeatureStore


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


MLFLOW_PREDICT_URL = "http://103.82.133.158:30051/invocations"


class FeatureEngineeringFunction(KeyedProcessFunction):

    def open(self, runtime_context: RuntimeContext):
        state_desc = MapStateDescriptor("txn_state", Types.STRING(), Types.PICKLED_BYTE_ARRAY())
        self.txn_state = runtime_context.get_map_state(state_desc)
        self.txn_window_secs = 7200
        self.store = FeatureStore(repo_path="/opt/flink/feature_store/")

    def process_element(self, value, ctx: 'KeyedProcessFunction.Context'):
        try:
            event = json.loads(value)
            after = event.get("after", {})
            customer_id = after.get("customer_id")
            merchant_id = after.get("merchant_id")
            amt = after.get("amt")
            lat, lon = after.get("lat"), after.get("lon")
            date_str = after.get("date")
            time_str = after.get("time")

            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            timestamp = int(dt.timestamp())

            if not (customer_id and merchant_id and timestamp):
                return

            # Step 1: Get feature from Feast
            features = self.store.get_online_features(
                features=[
                    "d_customer_feature:gender", "d_customer_feature:age", "d_customer_feature:age_group_encoded",
                    "d_customer_feature:population_level", "d_customer_feature:income_level", "d_customer_feature:is_young_state",
                    "d_customer_feature:norm_poverty_rate", "d_customer_feature:norm_unemployment_rate",
                    "d_customer_feature:norm_poverty_per_unemployed", "d_customer_feature:lat", "d_customer_feature:lon",
                    "d_customer_feature:avg_txn_last_7d", "d_customer_feature:avg_amt_last_7d", "d_customer_feature:sum_amt_last_7d",
                    "d_customer_feature:num_txn_last_7d", "d_customer_feature:is_young", "d_customer_feature:is_elder",
                    "d_customer_feature:is_urban", "d_merchant_feature:category_encoded"
                ],
                entity_rows=[{"customer_id": customer_id, "merchant_id": merchant_id}],
                full_feature_names=False
            ).to_dict()
            after.update({k: v[0] for k, v in features.items()})

            # Step 2: Time features
            hour, dow = dt.hour, dt.weekday()
            after.update({
                "hour": hour,
                "dayofweek": dow,
                "month": dt.month,
                "is_night": int(hour < 6 or hour >= 22),
                "is_weekend": int(dow >= 5),
                "is_peak_hour": int(6 <= hour <= 10 or 16 <= hour <= 19),
                "log_amt": math.log1p(amt),
                "is_high_amt": int(amt > 500)
            })

            # Step 3: Distance
            home_lat = after.get("lat")
            home_lon = after.get("lon")
            if lat and lon and home_lat and home_lon:
                dist = haversine_distance(lat, lon, home_lat, home_lon)
                after["distance_from_home"] = dist
                after["is_far_from_home"] = int(dist > 125)
            else:
                after["distance_from_home"] = 0
                after["is_far_from_home"] = 0

            # Step 4: History state
            txn_bytes = self.txn_state.get(customer_id)
            txn_deque = pickle.loads(txn_bytes) if txn_bytes else deque()
            while txn_deque and timestamp - txn_deque[0][0] > self.txn_window_secs:
                txn_deque.popleft()
            num_txn_last_2h = len(txn_deque)
            time_diff = timestamp - txn_deque[-1][0] if txn_deque else -1
            is_first_txn = int(not txn_deque)
            txn_deque.append((timestamp, amt))
            self.txn_state.put(customer_id, pickle.dumps(txn_deque))
            after.update({
                "num_txn_last_2h": num_txn_last_2h,
                "time_diff": time_diff,
                "is_first_txn": is_first_txn
            })

            # Step 5: Surge
            avg_amt = after.get("avg_amt_last_7d", 0)
            num_txn = after.get("num_txn_last_7d", 0)
            after["is_amt_surge"] = int(num_txn > 0 and amt > avg_amt * 2)

            # Step 6: Predict
            feature_columns = [
                "gender", "age", "age_group_encoded", "population_level", "income_level", "is_young_state",
                "norm_poverty_rate", "norm_unemployment_rate", "norm_poverty_per_unemployed", "category_encoded",
                "hour", "dayofweek", "is_night", "is_weekend", "month", "is_peak_hour", "log_amt", "is_high_amt",
                "distance_from_home", "is_far_from_home", "num_txn_last_2h", "time_diff", "is_first_txn",
                "num_txn_last_7d", "avg_txn_last_7d", "avg_amt_last_7d", "sum_amt_last_7d", "is_amt_surge",
                "is_young", "is_elder", "is_urban"
            ]
            input_data = {
                "dataframe_split": {
                    "columns": feature_columns,
                    "data": [[after.get(col, 0) for col in feature_columns]]
                }
            }
            response = requests.post(
                MLFLOW_PREDICT_URL,
                headers={"Content-Type": "application/json"},
                json=input_data,
                timeout=3
            )
            prediction = response.json()["predictions"][0]
            after["is_fraud"] = int(prediction)

            yield json.dumps(after)

        except Exception as e:
            import traceback
            print(f"[ERROR] {str(e)}\n{traceback.format_exc()}")


def main():
    env = StreamExecutionEnvironment.get_execution_environment()

    kafka_props = {
        'bootstrap.servers': 'kafka.kafka.svc.cluster.local:9092',
        'group.id': 'flink.fraud-detection.prediction',
        'auto.offset.reset': 'latest',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'SCRAM-SHA-256',
        'sasl.jaas.config': 'org.apache.kafka.common.security.scram.ScramLoginModule required username="kafka" password="kafka";',
        'ssl.truststore.location': '/opt/flink/secrets/kafka.truststore.jks',
        'ssl.truststore.password': 'changeit',
        'ssl.keystore.location': '/opt/flink/secrets/kafka.keystore.jks',
        'ssl.keystore.password': 'changeit'
    }

    source = FlinkKafkaConsumer(
        topics='financial-ops.core.transaction',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    sink = FlinkKafkaProducer(
        topic='predicted-transaction',
        serialization_schema=SimpleStringSchema(),
        producer_config=kafka_props
    )

    env.add_source(source) \
        .key_by(lambda x: json.loads(x).get("after", {}).get("customer_id", "")) \
        .process(FeatureEngineeringFunction(), output_type=Types.STRING()) \
        .add_sink(sink)

    env.execute("Real-Time Credit Card Fraud Detection")


if __name__ == '__main__':
    main()
    
