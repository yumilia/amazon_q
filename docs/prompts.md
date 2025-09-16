# 📚 Prompts utilizados no Amazon Q Developer

Este documento reúne todos os prompts usados na construção do **FinAPI** durante o desafio **Amazon Q Developer Quest – TDC São Paulo 2025**.  
Eles foram enviados ao **Amazon Q Developer (VS Code)** para gerar, refatorar e ajustar o projeto.

---

## 🧱 Estrutura inicial (CDK + Lambda + API + DynamoDB)

Quero construir uma aplicação de finanças pessoais chamada FinAPI.  
Ela deve ter uma API REST no API Gateway com três rotas principais:
- POST /tx para registrar uma transação
- GET /tx?month=YYYY-MM para listar as transações de um mês
- GET /report/monthly?month=YYYY-MM para gerar um relatório mensal

As rotas devem chamar uma função Lambda escrita em Python, e os dados precisam ser salvos em uma tabela do DynamoDB.  
Quero que a infraestrutura seja criada usando AWS CDK em Python.  
Gere também um requirements.txt e os passos de deploy com CDK.

---

## ✍️ Entrada do usuário (texto livre ou JSON)

Implemente no index.py uma função que aceite entrada em texto livre OU JSON:
- Texto: "50 restaurante almoço" → amount=50.0, category="restaurante", note="almoço"
- JSON: {"amount":50,"category":"restaurante","note":"almoço"}
Trate content-type e base64, e retorne 201 com o item salvo.  
Em caso de erro de parsing, retorne 400 com mensagem amigável.

---

## 💾 Persistência no DynamoDB

Modele itens na tabela finapi-transactions assim:
- pk = "user#anon#YYYY-MM"
- sk = "ts#<ISO-8601>"
Campos: amount (Number/Decimal), category (String), note (String), isoDate (String).  
Implemente put_item no POST /tx e query por pk no GET /tx e no relatório mensal.

---

## 📊 Relatório mensal

Implemente GET /report/monthly?month=YYYY-MM que:
- Busca itens por pk do mês
- Soma total, calcula ticket médio e agrega por categoria
- Retorna: {month,total,avg_ticket,by_category,count}

---

## 🧪 Testes automatizados com pytest

Adicione testes com pytest:
- test_parse_free_text: verifica parsing com ponto e vírgula como separador decimal
- test_create_transaction: use DummyTable ou override de get_table() para não acessar AWS; assegure que salva Decimal e categorias corretamente
Forneça comandos no README: `$env:PYTHONPATH="."` e `pytest -q`

---

## 🗺️ Diagrama de arquitetura (Mermaid)

Gere um bloco Mermaid para o README mostrando:
User -> API Gateway -> Lambda -> DynamoDB  
Use labels sem acento/ caracteres especiais para compatibilidade no GitHub.

---

## 🧰 IaC e ajustes do CDK

Revise a stack CDK:
- `code.from_asset("lambda_src")`, `handler="index.handler"`
- `table.grant_read_write_data(lambda_fn)`
- `api.root.add_resource("tx")` com métodos GET/POST
- `api.root.add_resource("report").add_resource("monthly")` GET
- `CfnOutput` com `api.url`

---

## 🔌 Integração MCP

Quero integrar um servidor MCP simples (filesystem) ao projeto. Crie:
- mcp.json referenciando `"npx @modelcontextprotocol/server-filesystem"`
- amazonq.json com metadados do projeto, ponte para mcp.json e comando de testes (`pytest -q`)
Explique onde colocar os arquivos e como validar com npx.

---

## 🧯 Depuração de erros no POST /tx

Se o POST /tx retornar 500, mostre como:
- Checar CloudWatch logs da Lambda (comandos aws logs)
- Ajustar parsing JSON vs texto livre
- Tratar isBase64Encoded e content-type  
Forneça exemplos de respostas 400 detalhadas para erros de parsing.

---

## 🧹 Refatoração guiada

Refatore index.py para:
- Extrair get_method_and_path compatível com REST e HTTP API
- Funções puras para parse e agregação (facilitar testes)
- get_table() lazy com override para testes  
Mostre diffs e explique trade-offs.

---

## 💲 Estimativa de custos (Etapa 4)

Estime custo mensal em sa-east-1 para:
- DynamoDB on-demand (até 10k req/mês)
- Lambda (até 100k invocações)
- API Gateway REST (até 50k chamadas)  
Produza tabela no README com estimativa e referências da calculadora.
---