from feast.data_format import ParquetFormat
from datetime import timedelta
from feast import FeatureView, FileSource, Entity, Field
from feast.types import Float32, Int64, String, Bool
from feast.value_type import ValueType

# 1. Khai b√°o Entity
customer = Entity(
    name="customer_id",
    value_type=ValueType.STRING,
    description="M√£ ƒë·ªãnh danh kh√°ch h√†ng"
)

# file_format=ParquetFormat()

# 2. Khai b√°o FileSource tr·ªè v·ªÅ MinIO
customer_feature_source = FileSource(
    name="d_customer_feature_source",
    path="s3://feast-offline-store/gold-zone/fraud_detection/d_customer_feature/partition=20250608",
    file_format=ParquetFormat(),
#    timestamp_field="event_timestamp",  # Ì†ΩÌªë File ph·∫£i c√≥ c·ªôt n√†y (ki·ªÉu timestamp)
 #   partition_column="partition"        # Ì†ΩÌø° partition=YYYYMMDD trong path
)

# 3. Khai b√°o FeatureView
customer_feature_view = FeatureView(
    name="d_customer_feature",
    entities=["customer_id"],
    ttl=timedelta(days=1),
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
    source=customer_feature_source,
    online=True,
)
