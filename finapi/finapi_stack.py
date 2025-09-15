from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
)
from constructs import Construct


class FinapiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
        table = dynamodb.Table(
            self,
            "TransactionsTable",
            partition_key=dynamodb.Attribute(
                name="pk", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Lambda Function
        lambda_fn = _lambda.Function(
            self,
            "FinapiFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda_src"),  # em vez de "lambda"
            environment={"TABLE_NAME": table.table_name},
        )

        # Grant permissions
        table.grant_read_write_data(lambda_fn)

        # API Gateway
        api = apigw.RestApi(self, "FinapiApi")

        # /tx resource
        tx_resource = api.root.add_resource("tx")
        tx_resource.add_method("GET", apigw.LambdaIntegration(lambda_fn))
        tx_resource.add_method("POST", apigw.LambdaIntegration(lambda_fn))

        # /report/monthly resource
        report_resource = api.root.add_resource("report")
        monthly_resource = report_resource.add_resource("monthly")
        monthly_resource.add_method("GET", apigw.LambdaIntegration(lambda_fn))
