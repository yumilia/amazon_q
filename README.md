# FinAPI - AWS CDK Project

API financeira com AWS CDK, Lambda, API Gateway e DynamoDB.

## Estrutura

- **API Gateway**: Endpoints REST
- **Lambda**: Python 3.12 para lógica de negócio
- **DynamoDB**: Tabela com pk/sk para transações

## Rotas

- `GET /tx` - Lista transações
- `POST /tx` - Cria transação
- `GET /report/monthly` - Relatório mensal

## Deploy

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Bootstrap CDK (primeira vez)
```bash
cdk bootstrap
```

### 3. Sintetizar template
```bash
cdk synth
```

### 4. Deploy
```bash
cdk deploy
```

### 5. Destruir recursos
```bash
cdk destroy
```

## Exemplo de uso

### Criar transação
```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/tx \
  -H "Content-Type: application/json" \
  -d '{"id": "tx001", "amount": 100.50, "description": "Compra"}'
```

### Listar transações
```bash
curl https://your-api-id.execute-api.region.amazonaws.com/prod/tx
```

### Relatório mensal
```bash
curl https://your-api-id.execute-api.region.amazonaws.com/prod/report/monthly
```