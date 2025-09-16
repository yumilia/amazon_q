# Prompts usados no projeto FinAPI

Este documento consolida os prompts utilizados durante o desenvolvimento do projeto, organizados por etapa do desafio.

---

## Etapa 1 – Criação do projeto

- Crie um projeto AWS CDK em Python com API Gateway, Lambda e DynamoDB (rotas /tx e /report/monthly).
- Implemente função para parsear entrada como "50 restaurante almoço".
- Gerar requirements.txt e passos de deploy com cdk.

---

## Etapa 2 – Testes automatizados

- Escreva testes com pytest para validar a função de parsing de texto livre.  
- Escreva testes para a criação de transações na Lambda (mockando o DynamoDB com moto).  

---

## Etapa 3 e 4 – MCP e estimativa de custo

- Configure um servidor MCP que use o AWS Knowledge MCP Server para buscar documentações e arquiteturas da AWS.  
- Proponha uma arquitetura AWS escalável e resiliente para o projeto FinAPI, que usa API Gateway, Lambda e DynamoDB.  
  Considere boas práticas de segurança, logging e baixo custo.  
  Se precisar, faça perguntas para ajustar o planejamento.

---