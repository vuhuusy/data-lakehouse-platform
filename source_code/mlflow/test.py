import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient(tracking_uri="http://103.82.20.169:30500")

exp_ids = [exp.experiment_id for exp in client.search_experiments()]
for eid in exp_ids:
    exp = client.get_experiment(eid)
    print(f"[{exp.experiment_id}] {exp.name} - {exp.lifecycle_stage}")
