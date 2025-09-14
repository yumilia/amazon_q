#!/usr/bin/env python3
import aws_cdk as cdk
from finapi.finapi_stack import FinapiStack

app = cdk.App()
FinapiStack(app, "FinapiStack")
app.synth()