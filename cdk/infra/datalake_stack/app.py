#!/usr/bin/env python3
import os

from aws_cdk import Tags
import aws_cdk as cdk

from stacks.StorageStack import StorageStack
# from data_pipline_stack.stacks import ProcessingStack


app = cdk.App()
datalakestorage = StorageStack(app, 
                      "DataPipelineStack",stage="staging",
    env=cdk.Environment(account='626635448755', region='eu-west-2')
    )
Tags.of(datalakestorage).add("StackType","DataLake")
# ProcessingStack(app, 
#                       "DataPipelineStack",stage="staging",
#     env=cdk.Environment(account='626635448755', region='eu-west-2')
#     )
# Tags.of(ProcessingStack).add("StackType","DataLake")
app.synth()
