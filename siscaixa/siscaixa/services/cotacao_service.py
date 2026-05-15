import requests

URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL"


def obter_cotacao():
    response = requests.get(URL, timeout=5)

    if response.status_code != 200:
        raise Exception("Erro ao consultar API")

    data = response.json()

    dolar = data["USDBRL"]

    return {
        "moeda": dolar["code"],
        "valor": dolar["bid"],
        "data": dolar["create_date"],
    }
