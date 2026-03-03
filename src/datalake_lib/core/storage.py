import boto3
from botocore.exceptions import ClientError
import json
import logging
_s3 = boto3.client("s3",region_name="eu-west-2")

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,        # show INFO and above
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def s3_writer(*,env:str,bucket_name:str,payload,duration,pre_fix,data_type):
    Bucket=f"{bucket_name}-{env.lower()}"
    Key=f"{pre_fix}/{duration}/data.{data_type}"

    if   isinstance(payload, (dict, list)):
        payload = json.dumps(payload).encode("utf-8")
    try:
        response = _s3.put_object(
            Bucket=Bucket,
            Key=Key,
            Body=payload,
        )
        logger.info(
            "object_written",
            extra={"bucket": Bucket, "key": Key, "env": env},
        )

    except ClientError:
        logger.exception(
            "s3_put_failed",
            extra={"bucket": Bucket, "key": Key, "env": env},
        )
        raise
    return f"s3://{Bucket}/{Key}"

def s3_reader(*,env,bucket,prefix,payload):
    pass
    return 0
