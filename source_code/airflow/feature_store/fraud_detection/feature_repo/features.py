from datetime import timedelta
from google.protobuf.duration_pb2 import Duration
from feast import Entity, Feature, FeatureView, ValueType
from feast_trino import TrinoSource

# Define TrinoSources
d_customer_source = TrinoSource(
    table_ref="delta_lake.default.v_d_customer_feature",
    event_timestamp_column="event_timestamp",
)

d_merchant_source = TrinoSource(
    table_ref="delta_lake.default.v_d_merchant_feature",
    event_timestamp_column="event_timestamp",
)

# Define Entities
d_customer_entity = Entity(
    name="customer_id",
    value_type=ValueType.STRING,
    description="Customer ID",
)

d_merchant_entity = Entity(
    name="merchant_id",
    value_type=ValueType.STRING,
    description="Merchant ID",
)

# Define FeatureViews
d_customer_fv = FeatureView(
    name="d_customer_feature",
    entities=["customer_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="age", dtype=ValueType.INT64),
        Feature(name="age_group_encoded", dtype=ValueType.INT64),
        Feature(name="is_young", dtype=ValueType.INT64),
        Feature(name="is_elder", dtype=ValueType.INT64),
        Feature(name="gender", dtype=ValueType.INT64),
        Feature(name="city", dtype=ValueType.STRING),
        Feature(name="state", dtype=ValueType.STRING),
        Feature(name="lat", dtype=ValueType.FLOAT),
        Feature(name="lon", dtype=ValueType.FLOAT),
        Feature(name="is_urban", dtype=ValueType.INT64),
        Feature(name="population_level", dtype=ValueType.INT64),
        Feature(name="income_level", dtype=ValueType.INT64),
        Feature(name="is_young_state", dtype=ValueType.INT64),
        Feature(name="norm_poverty_rate", dtype=ValueType.FLOAT),
        Feature(name="norm_unemployment_rate", dtype=ValueType.FLOAT),
        Feature(name="norm_poverty_per_unemployed", dtype=ValueType.FLOAT),
        Feature(name="avg_txn_last_7d", dtype=ValueType.FLOAT),
        Feature(name="avg_amt_last_7d", dtype=ValueType.FLOAT),
        Feature(name="sum_amt_last_7d", dtype=ValueType.FLOAT),
        Feature(name="num_txn_last_7d", dtype=ValueType.FLOAT),
    ],
    online=True,
    batch_source=d_customer_source
)

d_merchant_fv = FeatureView(
    name="d_merchant_feature",
    entities=["merchant_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="category_encoded", dtype=ValueType.INT64)
    ],
    online=True,
    batch_source=d_merchant_source
)
