import sys
import os
import math
from concurrent import futures

import grpc

# ============================================================
# LOCALIZAR OS ARQUIVOS GERADOS DO gRPC
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_DIR = os.path.join(
    BASE_DIR,
    "grpc_client",
    "generated"
)

sys.path.insert(0, GENERATED_DIR)

import shipping_pb2
import shipping_pb2_grpc


# ============================================================
# CONFIGURAÇÃO DO SERVIDOR
# ============================================================

SERVER_TEAM = "S01"


# ============================================================
# SERVIÇO gRPC
# ============================================================

class ShippingService(shipping_pb2_grpc.ShippingServiceServicer):

    # ========================================================
    # HEALTH
    # ========================================================

    def Health(self, request, context):

        return shipping_pb2.HealthResponse(
            status="SERVING",
            server_team=SERVER_TEAM
        )

    # ========================================================
    # CALCULATE SHIPPING
    # ========================================================

    def CalculateShipping(self, request, context):

        # ----------------------------------------------------
        # Metadata obrigatória
        # ----------------------------------------------------

        metadata = dict(context.invocation_metadata())

        if "x-client-team" not in metadata:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "MISSING_CLIENT_TEAM"
            )

        # ----------------------------------------------------
        # request_id
        # ----------------------------------------------------

        if not request.request_id:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "MISSING_REQUEST_ID"
            )

        # ----------------------------------------------------
        # Peso
        # ----------------------------------------------------

        if request.weight_grams < 1 or request.weight_grams > 30000:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "INVALID_WEIGHT"
            )

        # ----------------------------------------------------
        # Zona
        # ----------------------------------------------------

        if request.zone == shipping_pb2.SHIPPING_ZONE_UNSPECIFIED:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "INVALID_ZONE"
            )

        # ----------------------------------------------------
        # Modo
        # ----------------------------------------------------

        if request.mode == shipping_pb2.SHIPPING_MODE_UNSPECIFIED:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "INVALID_MODE"
            )

        # ----------------------------------------------------
        # Tarifas base
        # ----------------------------------------------------

        base_prices = {

            (
                shipping_pb2.SHIPPING_ZONE_LOCAL,
                shipping_pb2.SHIPPING_MODE_STANDARD
            ): 1000,

            (
                shipping_pb2.SHIPPING_ZONE_LOCAL,
                shipping_pb2.SHIPPING_MODE_EXPRESS
            ): 1600,

            (
                shipping_pb2.SHIPPING_ZONE_REGIONAL,
                shipping_pb2.SHIPPING_MODE_STANDARD
            ): 1800,

            (
                shipping_pb2.SHIPPING_ZONE_REGIONAL,
                shipping_pb2.SHIPPING_MODE_EXPRESS
            ): 2800,

            (
                shipping_pb2.SHIPPING_ZONE_NATIONAL,
                shipping_pb2.SHIPPING_MODE_STANDARD
            ): 3000,

            (
                shipping_pb2.SHIPPING_ZONE_NATIONAL,
                shipping_pb2.SHIPPING_MODE_EXPRESS
            ): 4500,
        }

        # ----------------------------------------------------
        # Buscar tarifa base
        # ----------------------------------------------------

        base_price = base_prices[
            (request.zone, request.mode)
        ]

        # ----------------------------------------------------
        # Adicional por kg iniciado
        # ----------------------------------------------------

        if request.mode == shipping_pb2.SHIPPING_MODE_STANDARD:
            additional_per_kg = 400
        else:
            additional_per_kg = 600

        # ----------------------------------------------------
        # Quilogramas cobrados
        #
        # ceil(weight_grams / 1000)
        # ----------------------------------------------------

        charged_kg = math.ceil(
            request.weight_grams / 1000
        )

        # ----------------------------------------------------
        # Cálculo do preço
        # ----------------------------------------------------

        price_cents = (
            base_price
            + charged_kg * additional_per_kg
        )

        # ----------------------------------------------------
        # Prazo estimado
        # ----------------------------------------------------

        estimated_days = {

            (
                shipping_pb2.SHIPPING_ZONE_LOCAL,
                shipping_pb2.SHIPPING_MODE_STANDARD
            ): 2,

            (
                shipping_pb2.SHIPPING_ZONE_LOCAL,
                shipping_pb2.SHIPPING_MODE_EXPRESS
            ): 1,

            (
                shipping_pb2.SHIPPING_ZONE_REGIONAL,
                shipping_pb2.SHIPPING_MODE_STANDARD
            ): 4,

            (
                shipping_pb2.SHIPPING_ZONE_REGIONAL,
                shipping_pb2.SHIPPING_MODE_EXPRESS
            ): 2,

            (
                shipping_pb2.SHIPPING_ZONE_NATIONAL,
                shipping_pb2.SHIPPING_MODE_STANDARD
            ): 7,

            (
                shipping_pb2.SHIPPING_ZONE_NATIONAL,
                shipping_pb2.SHIPPING_MODE_EXPRESS
            ): 3,
        }

        days = estimated_days[
            (request.zone, request.mode)
        ]

        # ----------------------------------------------------
        # Resposta
        # ----------------------------------------------------

        return shipping_pb2.ShippingResponse(
            request_id=request.request_id,
            price_cents=price_cents,
            estimated_days=days,
            server_team=SERVER_TEAM
        )


# ============================================================
# INICIAR SERVIDOR
# ============================================================

def serve():

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    shipping_pb2_grpc.add_ShippingServiceServicer_to_server(
        ShippingService(),
        server
    )

    server.add_insecure_port(
        "[::]:50051"
    )

    server.start()

    print("=" * 60)
    print("CONECTASHOP - SERVIDOR gRPC DE TESTE")
    print("=" * 60)
    print("Servidor: S01")
    print("Target: localhost:50051")
    print("=" * 60)
    print("Servidor aguardando conexões...")
    print("Pressione CTRL+C para parar.")
    print("=" * 60)

    try:
        server.wait_for_termination()

    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.stop(0)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    serve()