from feast.data_format import ParquetFormat
from datetime import timedelta
from feast import FeatureView, FileSource, Entity, Field
from feast.types import Float32, Int64, String, Bool
from feast.value_type import ValueType

# 1. Khai báo Entity
customer = Entity(
    name="customer_id",
    value_type=ValueType.STRING,
    description="Mã định danh khách hàng"
)

# file_format=ParquetFormat()

# 2. Khai báo FileSource trỏ về MinIO
customer_feature_source = FileSource(
    name="d_customer_feature_source",
    path="s3://gold-zone/fraud_detection/d_customer_feature/partition=20250608",
    file_format=ParquetFormat(),
#    timestamp_field="event_timestamp",  # ������ File phải có cột này (kiểu timestamp)
 #   partition_column="partition"        # ������ partition=YYYYMMDD trong path
)

# 3. Khai báo FeatureView
customer_feature_view = FeatureView(
    name="d_customer_feature",
    entities=[customer],
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
