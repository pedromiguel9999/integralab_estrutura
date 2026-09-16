import os
import uuid
import time
import requests


# ============================================================
# CONFIGURAÇÃO
# ============================================================

REST_BASE_URL = os.getenv(
    "REST_BASE_URL",
    "http://localhost:5000"
)

CLIENT_TEAM = os.getenv(
    "CLIENT_TEAM",
    "CLIENTE"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def generate_request_id():
    """Gera um ID único para cada requisição."""
    return str(uuid.uuid4())


def log_result(
    operation,
    method,
    url,
    request_id,
    status,
    response_data,
    duration_ms,
    expected_status
):
    """
    Mostra o resultado do teste no terminal.
    """

    result = "PASS" if status == expected_status else "FAIL"

    print("=" * 70)
    print(f"PROTOCOLO : REST")
    print(f"OPERAÇÃO  : {operation}")
    print(f"MÉTODO    : {method}")
    print(f"TARGET    : {url}")
    print(f"REQUEST ID: {request_id}")
    print(f"STATUS    : {status}")
    print(f"RESPOSTA  : {response_data}")
    print(f"DURAÇÃO   : {duration_ms:.2f} ms")
    print(f"RESULTADO : {result}")
    print("=" * 70)

    return result


def make_request(method, endpoint, operation, expected_status, json_data=None):
    """
    Executa uma requisição REST com os headers obrigatórios.
    """

    url = f"{REST_BASE_URL}{endpoint}"

    request_id = generate_request_id()

    headers = {
        "X-Client-Team": CLIENT_TEAM,
        "X-Request-ID": request_id,
        "Content-Type": "application/json"
    }

    start = time.perf_counter()

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            timeout=10
        )

        duration_ms = (time.perf_counter() - start) * 1000

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        return log_result(
            operation=operation,
            method=method,
            url=url,
            request_id=request_id,
            status=response.status_code,
            response_data=response_data,
            duration_ms=duration_ms,
            expected_status=expected_status
        )

    except requests.RequestException as error:

        duration_ms = (time.perf_counter() - start) * 1000

        print("=" * 70)
        print("PROTOCOLO : REST")
        print(f"OPERAÇÃO  : {operation}")
        print(f"TARGET    : {url}")
        print(f"REQUEST ID: {request_id}")
        print(f"ERRO      : {error}")
        print(f"DURAÇÃO   : {duration_ms:.2f} ms")
        print("RESULTADO : FAIL")
        print("=" * 70)

        return "FAIL"


# ============================================================
# TESTES R1–R5
# ============================================================

def test_r1():
    """
    R1:
    GET /api/v1/products/KB-100

    Esperado:
    HTTP 200
    unitPriceCents = 25990
    """

    return make_request(
        method="GET",
        endpoint="/api/v1/products/KB-100",
        operation="R1 - Buscar KB-100",
        expected_status=200
    )


def test_r2():
    """
    R2:
    GET /api/v1/products/XX-999

    Esperado:
    HTTP 404
    code = PRODUCT_NOT_FOUND
    """

    return make_request(
        method="GET",
        endpoint="/api/v1/products/XX-999",
        operation="R2 - Produto inexistente",
        expected_status=404
    )


def test_r3():
    """
    R3:
    2x KB-100
    1x MS-200

    Esperado:
    subtotal = 64970
    discount = 5%
    total = 61722
    """

    data = {
        "items": [
            {
                "sku": "KB-100",
                "quantity": 2
            },
            {
                "sku": "MS-200",
                "quantity": 1
            }
        ]
    }

    return make_request(
        method="POST",
        endpoint="/api/v1/quotes",
        operation="R3 - Cotação KB-100 + MS-200",
        expected_status=200,
        json_data=data
    )


def test_r4():
    """
    R4:
    1x MN-400

    Esperado:
    subtotal = 119990
    discount = 10%
    discountCents = 11999
    total = 107991
    """

    data = {
        "items": [
            {
                "sku": "MN-400",
                "quantity": 1
            }
        ]
    }

    return make_request(
        method="POST",
        endpoint="/api/v1/quotes",
        operation="R4 - Cotação MN-400",
        expected_status=200,
        json_data=data
    )


def test_r5():
    """
    R5:
    SKU inválido.

    Esperado:
    HTTP 422
    code = INVALID_PRODUCT
    """

    data = {
        "items": [
            {
                "sku": "XX-999",
                "quantity": 1
            }
        ]
    }

    return make_request(
        method="POST",
        endpoint="/api/v1/quotes",
        operation="R5 - SKU inválido",
        expected_status=422,
        json_data=data
    )


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print()
    print("=" * 70)
    print("CONECTASHOP - CLIENTE REST")
    print("=" * 70)
    print(f"REST_BASE_URL: {REST_BASE_URL}")
    print(f"CLIENT_TEAM  : {CLIENT_TEAM}")
    print("=" * 70)
    print()

    results = []

    results.append(("R1", test_r1()))
    results.append(("R2", test_r2()))
    results.append(("R3", test_r3()))
    results.append(("R4", test_r4()))
    results.append(("R5", test_r5()))

    print()
    print("=" * 70)
    print("RESUMO DOS TESTES REST")
    print("=" * 70)

    for test, result in results:
        print(f"{test}: {result}")

    print("=" * 70)


if __name__ == "__main__":
    main()