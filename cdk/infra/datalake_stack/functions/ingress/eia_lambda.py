# lambda_handler.py
import os
from datalake_lib.ingress.eia import fetch_eia
from datalake_lib.config.constants import bucket_configs,duration

def handler(event, context):
    env = os.environ.get("ENV", "staging")  # set via CDK
    bucket = os.environ["RAW_BUCKET"]
    key = fetch_eia(env, bucket)
    from datalake_lib.ingress.eia import fetch_eia
    fetch_eia(env="staging", bucket=bucket_configs["landing_bucket"],duration=duration)
    return {"status": "ok", "written_to": key}