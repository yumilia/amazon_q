import decimal
from lambda_src import index as mod


class DummyTable:
    def __init__(self):
        self.saved = None

    def put_item(self, Item):
        self.saved = Item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def query(self, **kwargs):
        return {"Items": [self.saved] if self.saved else []}


def test_create_transaction_texto_livre(monkeypatch):
    dummy = DummyTable()
    monkeypatch.setattr(mod, "_table_override", dummy)  # injeção

    payload = "50 restaurante almoço"
    result = mod.create_transaction(payload, event={})

    assert result["ok"] is True
    assert dummy.saved["category"] == "restaurante"
    assert float(dummy.saved["amount"]) == 50.0


def test_create_transaction_json(monkeypatch):
    dummy = DummyTable()
    monkeypatch.setattr(mod, "_table_override", dummy)

    payload = {"amount": 35, "category": "mercado", "note": "compras"}
    result = mod.create_transaction(payload, event={})

    assert result["ok"] is True
    assert dummy.saved["category"] == "mercado"
    assert float(dummy.saved["amount"]) == 35.0
