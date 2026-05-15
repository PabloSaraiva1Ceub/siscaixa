"""Teste de integração da API de cotação."""

from siscaixa.services.cotacao_service import obter_cotacao


def test_api_retorna_cotacao():
    """
    Verifica se a API retorna
    os dados esperados.
    """
    resultado = obter_cotacao()

    assert resultado["moeda"] == "USD"

    assert float(resultado["valor"]) > 0

    assert resultado["data"] is not None
