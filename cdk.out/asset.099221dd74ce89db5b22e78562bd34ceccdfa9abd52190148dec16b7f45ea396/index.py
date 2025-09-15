import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    method = event['httpMethod']
    path = event['resource']
    
    if path == '/tx':
        if method == 'GET':
            return get_transactions()
        elif method == 'POST':
            return create_transaction(json.loads(event['body']))
    
    elif path == '/report/monthly':
        if method == 'GET':
            return get_monthly_report()
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'})
    }

def get_transactions():
    response = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }

def create_transaction(data):
    item = {
        'pk': f"tx#{data['id']}",
        'sk': datetime.now().isoformat(),
        'amount': data['amount'],
        'description': data.get('description', ''),
        'created_at': datetime.now().isoformat()
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 201,
        'body': json.dumps(item)
    }

def get_monthly_report():
    # Simplified monthly report
    response = table.scan()
    total = sum(float(item.get('amount', 0)) for item in response['Items'])
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'total_transactions': len(response['Items']),
            'total_amount': total,
            'month': datetime.now().strftime('%Y-%m')
        })
    }