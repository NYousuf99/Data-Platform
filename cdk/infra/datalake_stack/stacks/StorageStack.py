from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_s3 as s3
)
from constructs import Construct

class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,*,stage:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.stage = stage
        self.DURATIONS = {
            "one_week": Duration.days(7),
            "one_month": Duration.days(30),
            "six_months": Duration.days(30*6),
            "two_years": Duration.days(365*2),
            "three_years": Duration.days(365*3),
            "four_years": Duration.days(365*4),
            "five_years": Duration.days(365*5),
        }

        bucket_configs = [
            ("landing_bucket", "Data-Lake-Landing-Bucket", self.DURATIONS["one_month"]),
            ("raw_bronze_bucket", "Data-Lake-Raw-Bronze-Bucket", self.DURATIONS["five_years"]),
            ("clean_silver_bucket", "Data-Lake-Clean-Silver-Bucket", self.DURATIONS["three_years"]),
            ("transformation_gold_bucket", "Data-Lake-Transformation-Gold-Bucket", self.DURATIONS["three_years"]),
        ]

        for attr_name, bucket_id, expiration_duration in bucket_configs:
            setattr(
                self,
                attr_name,
                s3.Bucket(
                    self,
                    bucket_id,
                    bucket_name=f"{bucket_id.lower()}-{self.stage}",
                    public_read_access=False,
                    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                    enforce_ssl=True,
                    versioned=True,
                    encryption=s3.BucketEncryption.S3_MANAGED,
                    lifecycle_rules=[
                        s3.LifecycleRule(
                            id="ExpireOldVersions",
                            noncurrent_version_expiration=self.DURATIONS["one_month"]
                        ),
                        s3.LifecycleRule(
                            id="AbortMultipartUploads",
                            abort_incomplete_multipart_upload_after=self.DURATIONS["one_week"]
                        ),
                        s3.LifecycleRule(
                            id=f"{expiration_duration}-CleanUp",
                            expiration=expiration_duration
                        )
                    ],
                    removal_policy=RemovalPolicy.DESTROY,
                    auto_delete_objects=True,
                )
            )