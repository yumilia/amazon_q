import json, os, decimal, re
from datetime import datetime, timezone
import boto3
from boto3.dynamodb.conditions import Key

TABLE = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


def parse_free_text(body_str: str):
    # "50 restaurante almoço" -> 50.0, "restaurante", "almoço"
    tokens = body_str.strip().split()
    if not tokens:
        raise ValueError("Corpo vazio")
    # aceita vírgula como separador decimal
    amount = float(re.sub(",", ".", tokens[0]))
    category = tokens[1].lower() if len(tokens) > 1 else "outros"
    note = " ".join(tokens[2:]) if len(tokens) > 2 else ""
    return amount, category, note


def get_user_id(event):
    # MVP: usuário anônimo; troque por Cognito depois
    return "user#anon"


def create_tx(event):
    user = get_user_id(event)
    body = event.get("body") or ""
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    ctype = headers.get("content-type", "")

    try:
        # Se vier base64 (algumas integrações), decodifique (caso necessário)
        if event.get("isBase64Encoded"):
            import base64

            body = base64.b64decode(body).decode("utf-8", errors="replace")

        # Tenta JSON se (a) content-type indica JSON, ou (b) corpo começa com "{"
        data = None
        if "application/json" in ctype or (
            body.strip().startswith("{") and body.strip().endswith("}")
        ):
            data = json.loads(body)

        if data is not None:
            amount = float(data["amount"])
            category = str(data.get("category", "outros")).lower()
            note = str(data.get("note", ""))
            date_str = data.get("date")
        else:
            # Texto livre
            amount, category, note = parse_free_text(body)
            date_str = None

        now = (
            datetime.now(timezone.utc)
            if not date_str
            else datetime.fromisoformat(date_str).astimezone(timezone.utc)
        )
        ym = now.strftime("%Y-%m")
        ts = now.isoformat()

        item = {
            "pk": f"{user}#{ym}",
            "sk": f"ts#{ts}",
            "amount": decimal.Decimal(str(amount)),
            "category": category,
            "note": note,
            "isoDate": ts,
        }
        TABLE.put_item(Item=item)
        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": True, "saved": item}, cls=DecimalEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": False, "error": str(e)}),
        }


def list_tx(event):
    params = event.get("queryStringParameters") or {}
    month = params.get("month") or datetime.now(timezone.utc).strftime("%Y-%m")
    user = get_user_id(event)
    pk = f"{user}#{month}"
    res = TABLE.query(KeyConditionExpression=Key("pk").eq(pk))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"items": res.get("Items", [])}, cls=DecimalEncoder),
    }


def monthly_report(event):
    params = event.get("queryStringParameters") or {}
    month = params.get("month") or datetime.now(timezone.utc).strftime("%Y-%m")
    user = get_user_id(event)
    pk = f"{user}#{month}"
    res = TABLE.query(KeyConditionExpression=Key("pk").eq(pk))
    totals = {}
    total = decimal.Decimal("0")
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
