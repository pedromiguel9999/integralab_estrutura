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
    Mostra o resultado do teste no terminal
    e grava no arquivo integration.log.
    """

    result = "PASS" if status == expected_status else "FAIL"

    print("=" * 70)
    print("PROTOCOLO : REST")
    print(f"OPERAÇÃO  : {operation}")
    print(f"MÉTODO    : {method}")
    print(f"TARGET    : {url}")
    print(f"REQUEST ID: {request_id}")
    print(f"STATUS    : {status}")
    print(f"RESPOSTA  : {response_data}")
    print(f"DURAÇÃO   : {duration_ms:.2f} ms")
    print(f"RESULTADO : {result}")
    print("=" * 70)

    log_path = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "logs",
        "integration.log"
    )

    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        log_path,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{timestamp} | "
            f"protocol=REST | "
            f"operation={operation} | "
            f"method={method} | "
            f"target={url} | "
            f"request_id={request_id} | "
            f"status={status} | "
            f"duration_ms={duration_ms:.2f} | "
            f"result={result}\n"
        )

    return result


def make_request(
    method,
    endpoint,
    operation,
    expected_status,
    json_data=None
):
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

    url = f"{REST_BASE_URL}/api/v1/products/KB-100"
    request_id = generate_request_id()

    headers = {
        "X-Client-Team": CLIENT_TEAM,
        "X-Request-ID": request_id,
        "Content-Type": "application/json"
    }

    start = time.perf_counter()

    try:
        response = requests.get(
            url=url,
            headers=headers,
            timeout=10
        )

        duration_ms = (time.perf_counter() - start) * 1000
        response_data = response.json()

        status_ok = response.status_code == 200
        price_ok = response_data.get("unitPriceCents") == 25990

        result = "PASS" if status_ok and price_ok else "FAIL"

        print("=" * 70)
        print("PROTOCOLO : REST")
        print("OPERAÇÃO  : R1 - Buscar KB-100")
        print(f"STATUS    : {response.status_code}")
        print(f"RESPOSTA  : {response_data}")
        print(f"PREÇO OK  : {price_ok}")
        print(f"RESULTADO : {result}")
        print("=" * 70)

        return result

    except requests.RequestException as error:
        print(f"Erro no R1: {error}")
        return "FAIL"

def test_r2():
    """
    R2:
    GET /api/v1/products/XX-999

    Esperado:
    HTTP 404
    code = PRODUCT_NOT_FOUND
    """

    url = f"{REST_BASE_URL}/api/v1/products/XX-999"
    request_id = generate_request_id()

    headers = {
        "X-Client-Team": CLIENT_TEAM,
        "X-Request-ID": request_id,
        "Content-Type": "application/json"
    }

    start = time.perf_counter()

    try:
        response = requests.get(
            url=url,
            headers=headers,
            timeout=10
        )

        duration_ms = (time.perf_counter() - start) * 1000
        response_data = response.json()

        status_ok = response.status_code == 404
        code_ok = response_data.get("code") == "PRODUCT_NOT_FOUND"

        result = "PASS" if status_ok and code_ok else "FAIL"

        print("=" * 70)
        print("PROTOCOLO : REST")
        print("OPERAÇÃO  : R2 - Produto inexistente")
        print(f"STATUS    : {response.status_code}")
        print(f"RESPOSTA  : {response_data}")
        print(f"CODE OK   : {code_ok}")
        print(f"RESULTADO : {result}")
        print("=" * 70)

        return result

    except requests.RequestException as error:
        print(f"Erro no R2: {error}")
        return "FAIL"

def test_r3():
    """
    R3:
    2x KB-100
    1x MS-200

    Esperado:
    subtotalCents = 64970
    discountCents = 3248
    totalCents = 61722
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

    url = f"{REST_BASE_URL}/api/v1/quotes"
    request_id = generate_request_id()

    headers = {
        "X-Client-Team": CLIENT_TEAM,
        "X-Request-ID": request_id,
        "Content-Type": "application/json"
    }

    start = time.perf_counter()

    try:
        response = requests.post(
            url=url,
            headers=headers,
            json=data,
            timeout=10
        )

        duration_ms = (time.perf_counter() - start) * 1000
        response_data = response.json()

        status_ok = response.status_code == 200
        subtotal_ok = response_data.get("subtotalCents") == 64970
        discount_ok = response_data.get("discountCents") == 3248
        total_ok = response_data.get("totalCents") == 61722

        result = (
            "PASS"
            if status_ok
            and subtotal_ok
            and discount_ok
            and total_ok
            else "FAIL"
        )

        print("=" * 70)
        print("PROTOCOLO : REST")
        print("OPERAÇÃO  : R3 - Cotação KB-100 + MS-200")
        print(f"STATUS    : {response.status_code}")
        print(f"RESPOSTA  : {response_data}")
        print(f"SUBTOTAL OK : {subtotal_ok}")
        print(f"DESCONTO OK : {discount_ok}")
        print(f"TOTAL OK    : {total_ok}")
        print(f"RESULTADO   : {result}")
        print("=" * 70)

        return result

    except requests.RequestException as error:
        print(f"Erro no R3: {error}")
        return "FAIL"
def test_r4():
    """
    R4:
    1x MN-400

    Esperado:
    HTTP 200
    subtotalCents = 119990
    discountCents = 11999
    totalCents = 107991
    """

    data = {
        "items": [
            {
                "sku": "MN-400",
                "quantity": 1
            }
        ]
    }

    url = f"{REST_BASE_URL}/api/v1/quotes"
    request_id = generate_request_id()

    headers = {
        "X-Client-Team": CLIENT_TEAM,
        "X-Request-ID": request_id,
        "Content-Type": "application/json"
    }

    start = time.perf_counter()

    try:
        response = requests.post(
            url=url,
            headers=headers,
            json=data,
            timeout=10
        )

        duration_ms = (time.perf_counter() - start) * 1000
        response_data = response.json()

        status_ok = response.status_code == 200
        subtotal_ok = response_data.get("subtotalCents") == 119990
        discount_ok = response_data.get("discountCents") == 11999
        total_ok = response_data.get("totalCents") == 107991

        result = (
            "PASS"
            if status_ok
            and subtotal_ok
            and discount_ok
            and total_ok
            else "FAIL"
        )

        print("=" * 70)
        print("PROTOCOLO : REST")
        print("OPERAÇÃO  : R4 - Cotação MN-400")
        print(f"STATUS    : {response.status_code}")
        print(f"RESPOSTA  : {response_data}")
        print(f"SUBTOTAL OK : {subtotal_ok}")
        print(f"DESCONTO OK : {discount_ok}")
        print(f"TOTAL OK    : {total_ok}")
        print(f"RESULTADO   : {result}")
        print("=" * 70)

        return result

    except requests.RequestException as error:
        print(f"Erro no R4: {error}")
        return "FAIL"

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

    url = f"{REST_BASE_URL}/api/v1/quotes"
    request_id = generate_request_id()

    headers = {
        "X-Client-Team": CLIENT_TEAM,
        "X-Request-ID": request_id,
        "Content-Type": "application/json"
    }

    start = time.perf_counter()

    try:
        response = requests.post(
            url=url,
            headers=headers,
            json=data,
            timeout=10
        )

        duration_ms = (time.perf_counter() - start) * 1000
        response_data = response.json()

        status_ok = response.status_code == 422
        code_ok = response_data.get("code") == "INVALID_PRODUCT"

        result = "PASS" if status_ok and code_ok else "FAIL"

        print("=" * 70)
        print("PROTOCOLO : REST")
        print("OPERAÇÃO  : R5 - SKU inválido")
        print(f"STATUS    : {response.status_code}")
        print(f"RESPOSTA  : {response_data}")
        print(f"CODE OK   : {code_ok}")
        print(f"RESULTADO : {result}")
        print("=" * 70)

        return result

    except requests.RequestException as error:
        print(f"Erro no R5: {error}")
        return "FAIL"
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