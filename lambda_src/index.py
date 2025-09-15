import json, os, decimal, re, base64
from datetime import datetime, timezone

import boto3, os

_dynamo = boto3.resource("dynamodb")
_table_override = None  # usado só em testes


def get_table():
    global _table_override
    if _table_override is not None:
        return _table_override
    name = os.environ.get("TABLE_NAME", "TEST_TABLE")
    return _dynamo.Table(name)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


def parse_free_text(body_str: str):
    # Ex.: "50 restaurante almoço" -> 50.0, "restaurante", "almoço"
    tokens = body_str.strip().split()
    if not tokens:
        raise ValueError("Corpo vazio")
    amount = float(re.sub(",", ".", tokens[0]))
    category = tokens[1].lower() if len(tokens) > 1 else "outros"
    note = " ".join(tokens[2:]) if len(tokens) > 2 else ""
    return amount, category, note


def get_user_id(event):
    return "user#anon"  # MVP; depois troque por Cognito se quiser


def _parse_body(event):
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8", errors="replace")
    headers = {
        (k or "").lower(): (v or "") for k, v in (event.get("headers") or {}).items()
    }
    ctype = headers.get("content-type", "")
    # tenta JSON se indicar JSON ou se parecer JSON
    if "application/json" in ctype or (
        body.strip().startswith("{") and body.strip().endswith("}")
    ):
        try:
            return json.loads(body)  # dict
        except Exception:
            pass
    return body  # texto livre


def create_transaction(payload, event):
    # aceita dict (JSON) ou str (texto)
    if isinstance(payload, dict):
        amount = float(payload["amount"])
        category = str(payload.get("category", "outros")).lower()
        note = str(payload.get("note", ""))
        date_str = payload.get("date")
    else:
        amount, category, note = parse_free_text(str(payload))
        date_str = None

    now = (
        datetime.now(timezone.utc)
        if not date_str
        else datetime.fromisoformat(date_str).astimezone(timezone.utc)
    )
    ym = now.strftime("%Y-%m")
    ts = now.isoformat()

    item = {
        "pk": f"{get_user_id(event)}#{ym}",
        "sk": f"ts#{ts}",
        "amount": decimal.Decimal(str(amount)),
        "category": category,
        "note": note,
        "isoDate": ts,
    }
    get_table().put_item(Item=item)
    return {"ok": True, "saved": item}


def handler(event, context):
    """
    Se sua API tiver outras rotas (GET /tx, GET /report/monthly),
    você pode roteá-las aqui inspecionando event['httpMethod'] e event['path'].
    Para este fix imediato, tratamos o POST /tx.
    """
    try:
        method = event.get("httpMethod") or (
            event.get("requestContext", {}).get("http", {}) or {}
        ).get("method")
        path = event.get("path") or event.get("rawPath") or ""
        if method == "POST" and path.endswith("/tx"):
            payload = _parse_body(event)
            result = create_transaction(payload, event)
            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(result, cls=DecimalEncoder),
            }
        # mínimos para testes rápidos: listar e relatório (retornam vazio se não existirem outros handlers)
        if method == "GET" and path.endswith("/tx"):
            params = event.get("queryStringParameters") or {}
            month = params.get("month") or datetime.now(timezone.utc).strftime("%Y-%m")
            pk = f"{get_user_id(event)}#{month}"
            res = get_table().query(KeyConditionExpression=Key("pk").eq(pk))
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"items": res.get("Items", [])}, cls=DecimalEncoder),
            }
        if method == "GET" and path.endswith("/report/monthly"):
            params = event.get("queryStringParameters") or {}
            month = params.get("month") or datetime.now(timezone.utc).strftime("%Y-%m")
            pk = f"{get_user_id(event)}#{month}"
            res = get_table().query(KeyConditionExpression=Key("pk").eq(pk))
            totals, total = {}, decimal.Decimal("0")
            for it in res.get("Items", []):
                amt = decimal.Decimal(str(it.get("amount", 0)))
                cat = it.get("category", "outros")
                totals[cat] = totals.get(cat, decimal.Decimal("0")) + amt
                total += amt
            count = len(res.get("Items", []))
            report = {
                "month": month,
                "total": float(total),
                "avg_ticket": float(total / count) if count else 0.0,
                "by_category": {k: float(v) for k, v in totals.items()},
                "count": count,
            }
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(report),
            }
        # fallback
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Not found: {method} {path}"}),
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": False, "error": str(e)}),
        }
