import os
import sys
import time
import uuid
from datetime import datetime
import grpc

# Permite encontrar os arquivos gerados pelo protoc
GENERATED_DIR = os.path.join(
    os.path.dirname(__file__),
    "generated"
)

sys.path.insert(0, GENERATED_DIR)

import shipping_pb2
import shipping_pb2_grpc


def write_log(protocol, operation, target, request_id, status, duration, result):
    log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs",
        "integration.log"
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(
            f"{timestamp} | "
            f"protocol={protocol} | "
            f"operation={operation} | "
            f"target={target} | "
            f"request_id={request_id} | "
            f"status={status} | "
            f"duration_ms={duration} | "
            f"result={result}\n"
        )

# ============================================================
# CONFIGURAÇÃO
# ============================================================

GRPC_TARGET = os.getenv("GRPC_TARGET", "localhost:50051")
CLIENT_TEAM = os.getenv("CLIENT_TEAM", "CLIENTE")


# ============================================================
# REQUEST ID
# ============================================================

def generate_request_id():
    return f"req-{uuid.uuid4()}"


# ============================================================
# METADATA
# ============================================================

def get_metadata():
    return (
        ("x-client-team", CLIENT_TEAM),
    )


# ============================================================
# EXECUÇÃO DOS TESTES
# ============================================================

def run_tests():

    print("=" * 60)
    print("CONECTASHOP - CLIENTE gRPC")
    print("=" * 60)
    print(f"Target: {GRPC_TARGET}")
    print(f"Client Team: {CLIENT_TEAM}")
    print("=" * 60)

    results = []

    channel = grpc.insecure_channel(GRPC_TARGET)
    stub = shipping_pb2_grpc.ShippingServiceStub(channel)

   # ========================================================
# G1 - HEALTH
# ========================================================

print("\n[G1] Health()")

request_id = generate_request_id()
start = time.perf_counter()

try:
    response = stub.Health(
        shipping_pb2.HealthRequest(),
        metadata=get_metadata()
    )

    duration = int((time.perf_counter() - start) * 1000)

    passed = response.status == "SERVING"

    write_log(
        "gRPC",
        "G1 Health",
        target,
        request_id,
        response.status,
        duration,
        "PASS" if passed else "FAIL"
    )

    print(f"Status: {response.status}")
    print(f"Server Team: {response.server_team}")
    print(f"Request ID: {request_id}")
    print(f"Duration: {duration} ms")
    print(f"Resultado: {'PASS' if passed else 'FAIL'}")

    results.append(("G1", passed))

except grpc.RpcError as e:

    duration = int((time.perf_counter() - start) * 1000)

    write_log(
        "gRPC",
        "G1 Health",
        target,
        request_id,
        e.code().name,
        duration,
        "FAIL"
    )

    print(f"Erro: {e.code().name}")
    print(f"Detalhes: {e.details()}")
    print(f"Duration: {duration} ms")
    print("Resultado: FAIL")

    results.append(("G1", False))

    # ========================================================
    # G2 - 1500g LOCAL STANDARD
    # ========================================================

    print("\n[G2] CalculateShipping()")

request_id = generate_request_id()

request = shipping_pb2.ShippingRequest(
    request_id=request_id,
    weight_grams=1500,
    zone=shipping_pb2.SHIPPING_ZONE_LOCAL,
    mode=shipping_pb2.SHIPPING_MODE_STANDARD,
)

start = time.perf_counter()

try:
    response = stub.CalculateShipping(
        request,
        metadata=get_metadata()
    )

    duration = int((time.perf_counter() - start) * 1000)

    passed = (
        response.request_id == request_id
        and response.price_cents == 1800
        and response.estimated_days == 2
    )

    write_log(
        "gRPC",
        "G2 CalculateShipping",
        target,
        request_id,
        "OK",
        duration,
        "PASS" if passed else "FAIL"
    )

    print(f"Request ID: {response.request_id}")
    print(f"Price: {response.price_cents} cents")
    print(f"Estimated Days: {response.estimated_days}")
    print(f"Server Team: {response.server_team}")
    print(f"Duration: {duration} ms")
    print(f"Resultado: {'PASS' if passed else 'FAIL'}")

    results.append(("G2", passed))

except grpc.RpcError as e:

    duration = int((time.perf_counter() - start) * 1000)

    write_log(
        "gRPC",
        "G2 CalculateShipping",
        target,
        request_id,
        e.code().name,
        duration,
        "FAIL"
    )

    print(f"Erro: {e.code().name}")
    print(f"Detalhes: {e.details()}")
    print(f"Duration: {duration} ms")
    print("Resultado: FAIL")

    results.append(("G2", False))

    # ========================================================
    # G3 - 2500g REGIONAL EXPRESS
    # ========================================================

    print("\n[G3] CalculateShipping()")

request_id = generate_request_id()

request = shipping_pb2.ShippingRequest(
    request_id=request_id,
    weight_grams=2500,
    zone=shipping_pb2.SHIPPING_ZONE_REGIONAL,
    mode=shipping_pb2.SHIPPING_MODE_EXPRESS,
)

start = time.perf_counter()

try:
    response = stub.CalculateShipping(
        request,
        metadata=get_metadata()
    )

    duration = int((time.perf_counter() - start) * 1000)

    passed = (
        response.request_id == request_id
        and response.price_cents == 4600
        and response.estimated_days == 2
    )

    write_log(
        "gRPC",
        "G3 CalculateShipping",
        target,
        request_id,
        "OK",
        duration,
        "PASS" if passed else "FAIL"
    )

    print(f"Request ID: {response.request_id}")
    print(f"Price: {response.price_cents} cents")
    print(f"Estimated Days: {response.estimated_days}")
    print(f"Server Team: {response.server_team}")
    print(f"Duration: {duration} ms")
    print(f"Resultado: {'PASS' if passed else 'FAIL'}")

    results.append(("G3", passed))

except grpc.RpcError as e:

    duration = int((time.perf_counter() - start) * 1000)

    write_log(
        "gRPC",
        "G3 CalculateShipping",
        target,
        request_id,
        e.code().name,
        duration,
        "FAIL"
    )

    print(f"Erro: {e.code().name}")
    print(f"Detalhes: {e.details()}")
    print(f"Duration: {duration} ms")
    print("Resultado: FAIL")

    results.append(("G3", False))oi

    # ========================================================
    # G4 - 1000g NATIONAL STANDARD
    # ========================================================

    print("\n[G4] 1000g - NATIONAL - STANDARD")

    request_id = generate_request_id()

    request = shipping_pb2.ShippingRequest(
        request_id=request_id,
        weight_grams=1000,
    zone=shipping_pb2.SHIPPING_ZONE_NATIONAL,
mode=shipping_pb2.SHIPPING_MODE_STANDARD,
    )

    start = time.perf_counter()

    try:

        response = stub.CalculateShipping(
            request,
            metadata=get_metadata()
        )
        
        duration = int((time.perf_counter() - start) * 1000)

        passed = (
            response.request_id == request_id
            and response.price_cents == 3400
            and response.estimated_days == 7
        )

        print(f"Price: {response.price_cents} cents")
        print(f"Estimated days: {response.estimated_days}")
        print(f"Request ID: {response.request_id}")
        print(f"Duration: {duration} ms")
        print(f"Resultado: {'PASS' if passed else 'FAIL'}")

        results.append(("G4", passed))

    except grpc.RpcError as e:

        duration = int((time.perf_counter() - start) * 1000)

        print(f"Erro: {e.code().name}")
        print(f"Detalhes: {e.details()}")
        print(f"Duration: {duration} ms")
        print("Resultado: FAIL")

        results.append(("G4", False))


    # ========================================================
    # G5 - PESO INVÁLIDO
    # ========================================================

    print("\n[G5] weight_grams = 0")

    request_id = generate_request_id()

    request = shipping_pb2.ShippingRequest(
        request_id=request_id,
        weight_grams=0,
    zone=shipping_pb2.SHIPPING_ZONE_LOCAL,
mode=shipping_pb2.SHIPPING_MODE_STANDARD,
    )

    start = time.perf_counter()

    try:

        # Esperamos que o servidor rejeite a requisição
        stub.CalculateShipping(
            request,
            metadata=get_metadata()
        )

        duration = int((time.perf_counter() - start) * 1000)

        print("Erro esperado não aconteceu.")
        print(f"Duration: {duration} ms")
        print("Resultado: FAIL")

        results.append(("G5", False))

    except grpc.RpcError as e:

        duration = int((time.perf_counter() - start) * 1000)

        passed = (
            e.code() == grpc.StatusCode.INVALID_ARGUMENT
            and e.details() == "INVALID_WEIGHT"
        )

        print(f"Status gRPC: {e.code().name}")
        print(f"Detalhes: {e.details()}")
        print(f"Duration: {duration} ms")
        print(f"Resultado: {'PASS' if passed else 'FAIL'}")

        results.append(("G5", passed))


    # ========================================================
    # RESUMO
    # ========================================================

    print("\n")
    print("=" * 60)
    print("RESUMO DOS TESTES gRPC")
    print("=" * 60)

    for test, passed in results:
        print(f"{test}: {'PASS' if passed else 'FAIL'}")

    total_pass = sum(1 for _, passed in results if passed)

    print("-" * 60)
    print(f"Resultado: {total_pass}/{len(results)} testes passaram")
    print("=" * 60)

    channel.close()


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":
    run_tests()