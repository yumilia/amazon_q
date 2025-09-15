import pytest
from lambda_src.index import parse_free_text


def test_parse_free_text_basico():
    amount, category, note = parse_free_text("50 restaurante almoço")
    assert amount == 50.0
    assert category == "restaurante"
    assert note == "almoço"


def test_parse_free_text_virgula_sem_nota():
    amount, category, note = parse_free_text("12,34 mercado")
    assert amount == 12.34
    assert category == "mercado"
    assert note == ""


def test_parse_free_text_vazio():
    with pytest.raises(ValueError):
        parse_free_text("   ")
