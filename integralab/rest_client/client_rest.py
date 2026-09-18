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


def write_log(
    operation,
    method,
    url,
    request_id,
    status,
    response_data,
    duration_ms,
    result
):
    """Grava o resultado da requisição no integration.log."""

    log_path = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "logs",
        "integration.log"
    )

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

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
            f"response={response_data} | "
            f"duration_ms={duration_ms:.2f} | "
            f"result={result}\n"
        )


def print_result(
    operation,
    method,
    url,
    request_id,
    status,
    response_data,
    duration_ms,
    result
):
    """Mostra o resultado no terminal."""

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

    write_log(
        operation=operation,
        method=method,
        url=url,
        request_id=request_id,
        status=status,
        response_data=response_data,
        duration_ms=duration_ms,
        result=result
    )


# ============================================================
# TESTE R1
# ============================================================

def test_r1():
    """
    R1:
    GET /api/v1/products/KB-100

    Esperado:
    HTTP 200
    unitPriceCents = 25990
    """

    operation = "R1 - Buscar KB-100"
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

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        status_ok = response.status_code == 200
        price_ok = (
            isinstance(response_data, dict)
            and response_data.get("unitPriceCents") == 25990
        )

        result = "PASS" if status_ok and price_ok else "FAIL"

        print_result(
            operation,
            "GET",
            url,
            request_id,
            response.status_code,
            response_data,
            duration_ms,
            result
        )

        return result

    except requests.RequestException as error:

        duration_ms = (time.perf_counter() - start) * 1000
        result = "FAIL"

        print_result(
            operation,
            "GET",
            url,
            request_id,
            "REQUEST_ERROR",
            str(error),
            duration_ms,
            result
        )

        return result


# ============================================================
# TESTE R2
# ============================================================

def test_r2():
    """
    R2:
    GET /api/v1/products/XX-999

    Esperado:
    HTTP 404
    code = PRODUCT_NOT_FOUND
    """

    operation = "R2 - Produto inexistente"
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

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        status_ok = response.status_code == 404
        code_ok = (
            isinstance(response_data, dict)
            and response_data.get("code") == "PRODUCT_NOT_FOUND"
        )

        result = "PASS" if status_ok and code_ok else "FAIL"

        print_result(
            operation,
            "GET",
            url,
            request_id,
            response.status_code,
            response_data,
            duration_ms,
            result
        )

        return result

    except requests.RequestException as error:

        duration_ms = (time.perf_counter() - start) * 1000
        result = "FAIL"

        print_result(
            operation,
            "GET",
            url,
            request_id,
            "REQUEST_ERROR",
            str(error),
            duration_ms,
            result
        )

        return result


# ============================================================
# TESTE R3
# ============================================================

def test_r3():
    """
    R3:
    2x KB-100
    1x MS-200

    Esperado:
    HTTP 200
    subtotalCents = 64970
    discountCents = 3248
    totalCents = 61722
    """

    operation = "R3 - Cotação KB-100 + MS-200"

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

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        status_ok = response.status_code == 200

        subtotal_ok = (
            isinstance(response_data, dict)
            and response_data.get("subtotalCents") == 64970
        )

        discount_ok = (
            isinstance(response_data, dict)
            and response_data.get("discountCents") == 3248
        )

        total_ok = (
            isinstance(response_data, dict)
            and response_data.get("totalCents") == 61722
        )

        result = (
            "PASS"
            if status_ok
            and subtotal_ok
            and discount_ok
            and total_ok
            else "FAIL"
        )

        print_result(
            operation,
            "POST",
            url,
            request_id,
            response.status_code,
            response_data,
            duration_ms,
            result
        )

        return result

    except requests.RequestException as error:

        duration_ms = (time.perf_counter() - start) * 1000
        result = "FAIL"

        print_result(
            operation,
            "POST",
            url,
            request_id,
            "REQUEST_ERROR",
            str(error),
            duration_ms,
            result
        )

        return result


# ============================================================
# TESTE R4
# ============================================================

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

    operation = "R4 - Cotação MN-400"

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

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        status_ok = response.status_code == 200

        subtotal_ok = (
            isinstance(response_data, dict)
            and response_data.get("subtotalCents") == 119990
        )

        discount_ok = (
            isinstance(response_data, dict)
            and response_data.get("discountCents") == 11999
        )

        total_ok = (
            isinstance(response_data, dict)
            and response_data.get("totalCents") == 107991
        )

        result = (
            "PASS"
            if status_ok
            and subtotal_ok
            and discount_ok
            and total_ok
            else "FAIL"
        )

        print_result(
            operation,
            "POST",
            url,
            request_id,
            response.status_code,
            response_data,
            duration_ms,
            result
        )

        return result

    except requests.RequestException as error:

        duration_ms = (time.perf_counter() - start) * 1000
        result = "FAIL"

        print_result(
            operation,
            "POST",
            url,
            request_id,
            "REQUEST_ERROR",
            str(error),
            duration_ms,
            result
        )

        return result


# ============================================================
# TESTE R5
# ============================================================

def test_r5():
    """
    R5:
    SKU inválido.

    Esperado:
    HTTP 422
    code = INVALID_PRODUCT
    """

    operation = "R5 - SKU inválido"

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

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        status_ok = response.status_code == 422

        code_ok = (
            isinstance(response_data, dict)
            and response_data.get("code") == "INVALID_PRODUCT"
        )

        result = "PASS" if status_ok and code_ok else "FAIL"

        print_result(
            operation,
            "POST",
            url,
            request_id,
            response.status_code,
            response_data,
            duration_ms,
            result
        )

        return result

    except requests.RequestException as error:

        duration_ms = (time.perf_counter() - start) * 1000
        result = "FAIL"

        print_result(
            operation,
            "POST",
            url,
            request_id,
            "REQUEST_ERROR",
            str(error),
            duration_ms,
            result
        )

        return result


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