from feast import Field, FeatureView
from feast.types import Float32, Int64, String, Bool
from feast_trino import TrinoSource

# Khai báo nguồn Trino view
d_customer_source = TrinoSource(
    name="d_customer_feature_source",
    table="delta_lake.default.vw_d_customer_feature",
    timestamp_field="event_timestamp",
)

# Khai báo Feature View
d_customer_fv = FeatureView(
    name="d_customer_feature",
    entities=["customer_id"],
    ttl=None,
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="age_group_encoded", dtype=Int64),
        Field(name="is_young", dtype=Bool),
        Field(name="is_elder", dtype=Bool),
        Field(name="gender", dtype=String),
        Field(name="city", dtype=String),
        Field(name="state", dtype=String),
        Field(name="lat", dtype=Float32),
        Field(name="lon", dtype=Float32),
        Field(name="is_urban", dtype=Bool),
        Field(name="population_level", dtype=String),
        Field(name="income_level", dtype=String),
        Field(name="is_young_state", dtype=Bool),
        Field(name="norm_poverty_rate", dtype=Float32),
        Field(name="norm_unemployment_rate", dtype=Float32),
        Field(name="norm_poverty_per_unemployed", dtype=Float32),
        Field(name="avg_txn_last_7d", dtype=Float32),
        Field(name="avg_amt_last_7d", dtype=Float32),
        Field(name="sum_amt_last_7d", dtype=Float32),
        Field(name="num_txn_last_7d", dtype=Int64),
    ],
    source=d_customer_source,
)
