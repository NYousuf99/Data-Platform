import os
import boto3
from botocore import *
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional


load_dotenv()

class EnvExceptionError(RuntimeError):
    def __init__(self,*,message):
        super().__init__(message)
 
@dataclass(froze=False)
class EnvConfig:
    name: str
    region: str
    stack_name: Optional[str] = None
    eia_api_key: Optional[str] = None
    nws_api_key: Optional[str] = None


def fetch_secrets(secret_name: str, region: str) ->str:
    session = boto3.client("secretsmanager",region_name=region)
    return session.get_secret_value(SecretId=secret_name)

@lru_cache(maxsize=1)
def load_env() -> EnvConfig:
    env = os.environ.get("ENV")
    region = os.environ.get("AWS_REGION")
    stack =  os.environ.get("STACK_NAME") 
    config = EnvConfig(name=env,region=region,stack_name=stack)

    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):

        config.eia_api_key = fetch_secrets(f"EIA_API_KEY_{env.upper()}",region=region)
        config.nws_api_key = fetch_secrets(f"NWS_API_KEY_{env.upper()}",region=region)        

    else:
        config.eia_api_key = os.environ.get(f"EIA_API_KEY_{env.upper()}")
        config.nws_api_key = os.environ.get(f"NWS_API_KEY_{env.upper()}")

    if "landing" in stack and not all([config.eia_api_key,config.nws_api_key]):
        raise EnvExceptionError(message=f"Failured to return api keys, zone:Landing, eia_api_key:{config.eia_api_key}, nws_api_key:{config.eia_api_key}")

    return config


EIA_URL = "https://api.eia.gov/v2/electricity"




