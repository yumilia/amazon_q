# FinAPI - Arquitetura Ultra Low-Cost

## Estimativa para Centenas de Transações

### Cenário Real: 300 transações/mês, 50 usuários

| Serviço | Uso | Custo/Mês |
|---------|-----|-----------|
| **API Gateway** | 300 requests | $0.001 |
| **Lambda** | 300 invocations, 128MB ARM64 | $0.06 |
| **DynamoDB** | 300 writes, 600 reads | $0.45 |
| **Cognito** | 50 MAU (free tier) | $0.00 |
| **CloudWatch** | Logs básicos | $0.50 |
| **Total** | | **$1.02/mês** |

## Stack CDK Minimal

```python
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_logs as logs
)

class FinapiUltraLowCostStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB On-Demand
        table = dynamodb.Table(
            self, "TransactionsTable",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.ON_DEMAND,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Lambda ARM64 mínimo
        lambda_fn = _lambda.Function(
            self, "FinapiFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            architecture=_lambda.Architecture.ARM_64,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
            memory_size=128,
            timeout=Duration.seconds(10),
            log_retention=logs.RetentionDays.THREE_DAYS,
            environment={"TABLE_NAME": table.table_name}
        )

        # API Gateway básico
        api = apigw.RestApi(self, "FinapiApi")
        
        tx_resource = api.root.add_resource("tx")
        tx_resource.add_method("GET", apigw.LambdaIntegration(lambda_fn))
        tx_resource.add_method("POST", apigw.LambdaIntegration(lambda_fn))
        
        report_resource = api.root.add_resource("report")
        monthly_resource = report_resource.add_resource("monthly")
        monthly_resource.add_method("GET", apigw.LambdaIntegration(lambda_fn))

        table.grant_read_write_data(lambda_fn)
```

## Lambda Otimizado

```python
import json, boto3, os
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    method = event['httpMethod']
    path = event['resource']
    
    if path == '/tx':
        return get_transactions() if method == 'GET' else create_transaction(event)
    elif path == '/report/monthly':
        return get_monthly_report()
    
    return {'statusCode': 404, 'body': json.dumps({'error': 'Not found'})}

def create_transaction(event):
    body = json.loads(event.get('body', '{}'))
    now = datetime.now(timezone.utc)
    
    item = {
        'pk': f"user#anon#{now.strftime('%Y-%m')}",
        'sk': f"tx#{now.isoformat()}",
        'amount': float(body['amount']),
        'category': body.get('category', 'outros'),
        'created_at': now.isoformat()
    }
    
    table.put_item(Item=item)
    return {'statusCode': 201, 'body': json.dumps({'success': True})}

def get_transactions():
    month = datetime.now(timezone.utc).strftime('%Y-%m')
    response = table.query(
        KeyConditionExpression='pk = :pk',
        ExpressionAttributeValues={':pk': f"user#anon#{month}"}
    )
    return {'statusCode': 200, 'body': json.dumps(response.get('Items', []))}

def get_monthly_report():
    month = datetime.now(timezone.utc).strftime('%Y-%m')
    response = table.query(
        KeyConditionExpression='pk = :pk',
        ExpressionAttributeValues={':pk': f"user#anon#{month}"}
    )
    
    items = response.get('Items', [])
    total = sum(item.get('amount', 0) for item in items)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'month': month,
            'total_transactions': len(items),
            'total_amount': total
        })
    }
```

## Otimizações Aplicadas

✅ **Lambda ARM64 128MB**: -20% custo + mínimo memory  
✅ **DynamoDB On-Demand**: Sem over-provisioning  
✅ **Logs 3 dias**: -90% custo logging  
✅ **Sem VPC/Cache**: Zero custos extras  
✅ **Código mínimo**: Menos compute time  

## Crescimento Futuro

- **< 1K tx/mês**: Manter atual (~$1-3/mês)
- **1K-5K tx/mês**: Considerar 256MB Lambda (~$5-15/mês)  
- **> 5K tx/mês**: DynamoDB Reserved Capacity (~$20-50/mês)

**Custo total estimado: $1-3/mês para centenas de transações**