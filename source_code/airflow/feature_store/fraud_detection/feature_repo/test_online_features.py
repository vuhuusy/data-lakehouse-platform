import time
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Tạo danh sách các entity
entity_rows = [
    {"customer_id": "C00000001"},
    {"customer_id": "C00000002"},
    {"customer_id": "C00000003"},
    {"customer_id": "C00000004"},
    {"customer_id": "C00000005"},
]

features = [
    "d_customer_feature:age",
    "d_customer_feature:gender",
    "d_customer_feature:lat",
    "d_customer_feature:lon",
]

# Đo thời gian truy xuất
start = time.time()
online_features = store.get_online_features(
    features=features,
    entity_rows=entity_rows
).to_df()
end = time.time()

print(online_features)
print(f"Thời gian truy xuất {len(entity_rows)} entity: {end - start:.4f} giây")
print(f"Tốc độ: {(end - start)/len(entity_rows):.4f} giây mỗi entity")
