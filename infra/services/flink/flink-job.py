import math
import json
import pickle
import asyncio
import aiohttp
from datetime import datetime
from collections import deque

from cachetools import TTLCache
from feast import FeatureStore

from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import AsyncFunction, RuntimeContext
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.functions import AsyncDataStream


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


class AsyncFraudDetector(AsyncFunction):
    def __init__(self):
        self.txn_window_secs = 7200

    def open(self, runtime_context: RuntimeContext):
        self.store = FeatureStore(repo_path="/opt/flink/feature_store/")
        self.session = aiohttp.ClientSession()
        self.txn_state = {}
        self.feast_cache = TTLCache(maxsize=10000, ttl=300)

    async def fetch_features(self, customer_id, merchant_id):
        key = (customer_id, merchant_id)
        if key in self.feast_cache:
            return self.feast_cache[key]
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
        result = {k: v[0] for k, v in features.items()}
        self.feast_cache[key] = result
        return result

    async def predict(self, feature_dict):
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
                "data": [[feature_dict.get(col, 0) for col in feature_columns]]
            }
        }
        async with self.session.post(
            "http://103.82.133.158:30051/invocations",
            json=input_data,
            timeout=3
        ) as response:
            result = await response.json()
            return int(result["predictions"][0])

    async def async_invoke(self, input_value, result_future):
        start_time = asyncio.get_event_loop().time()
        try:
            event = json.loads(input_value)
            after = event.get("after", {})
            customer_id = after.get("customer_id")
            merchant_id = after.get("merchant_id")
            amt = after.get("amt")
            lat, lon = after.get("lat"), after.get("lon")
            date_str, time_str = after.get("date"), after.get("time")

            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            timestamp = int(dt.timestamp())

            features = await self.fetch_features(customer_id, merchant_id)
            after.update(features)

            after.update({
                "hour": dt.hour,
                "dayofweek": dt.weekday(),
                "month": dt.month,
                "is_night": int(dt.hour < 6 or dt.hour >= 22),
                "is_weekend": int(dt.weekday() >= 5),
                "is_peak_hour": int(6 <= dt.hour <= 10 or 16 <= dt.hour <= 19),
                "log_amt": math.log1p(amt),
                "is_high_amt": int(amt > 500)
            })

            home_lat = after.get("lat")
            home_lon = after.get("lon")
            if lat and lon and home_lat and home_lon:
                dist = haversine_distance(lat, lon, home_lat, home_lon)
                after["distance_from_home"] = dist
                after["is_far_from_home"] = int(dist > 125)

            txn_deque = self.txn_state.get(customer_id, deque())
            txn_deque = deque(filter(lambda t: timestamp - t[0] <= self.txn_window_secs, txn_deque))
            after["num_txn_last_2h"] = len(txn_deque)
            after["time_diff"] = timestamp - txn_deque[-1][0] if txn_deque else -1
            after["is_first_txn"] = int(not txn_deque)
            txn_deque.append((timestamp, amt))
            self.txn_state[customer_id] = txn_deque

            avg_amt = after.get("avg_amt_last_7d", 0)
            num_txn = after.get("num_txn_last_7d", 0)
            after["is_amt_surge"] = int(num_txn > 0 and amt > avg_amt * 2)

            is_fraud = await self.predict(after)
            after["is_fraud"] = is_fraud

            result_future.complete(json.dumps(after))
        except Exception as e:
            result_future.complete(json.dumps({"error": str(e)}))
        
        finally:
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000
            print(f"[INFO] Processed record in {latency_ms:.2f} ms")


def main():
    env = StreamExecutionEnvironment.get_execution_environment()

    kafka_props = {
        'bootstrap.servers': 'kafka.kafka.svc.cluster.local:9092',
        'group.id': 'flink.fraud-detection.async',
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

    fraud_sink = FlinkKafkaProducer(
        topic='fraud-transaction',
        serialization_schema=SimpleStringSchema(),
        producer_config=kafka_props
    )


    stream = env.add_source(source)

    processed = AsyncDataStream.unordered_wait(
        stream,
        AsyncFraudDetector(),
        timeout=10000,
        capacity=100
    )

    fraud_only = processed.filter(
        lambda record: json.loads(record).get("is_fraud") == 1
    )


    processed.add_sink(sink)
    fraud_only.add_sink(fraud_sink)
    env.execute("Realtime Async Fraud Detection")


if __name__ == '__main__':
    main()
