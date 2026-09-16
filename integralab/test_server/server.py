from flask import Flask, request, jsonify

app = Flask(__name__)


# ============================================================
# CATÁLOGO FIXO DA ATIVIDADE
# ============================================================

PRODUCTS = {
    "KB-100": {
        "sku": "KB-100",
        "name": "Teclado Mecânico",
        "unitPriceCents": 25990,
        "available": True
    },
    "MS-200": {
        "sku": "MS-200",
        "name": "Mouse Sem Fio",
        "unitPriceCents": 12990,
        "available": True
    },
    "HD-300": {
        "sku": "HD-300",
        "name": "Headset USB",
        "unitPriceCents": 19990,
        "available": True
    },
    "MN-400": {
        "sku": "MN-400",
        "name": "Monitor 27",
        "unitPriceCents": 119990,
        "available": True
    }
}


# ============================================================
# VERIFICAÇÃO DOS HEADERS
# ============================================================

def check_headers():

    client_team = request.headers.get("X-Client-Team")
    request_id = request.headers.get("X-Request-ID")

    if not client_team or not request_id:
        return jsonify({
            "code": "MISSING_REQUIRED_HEADER",
            "message": "Required header missing",
            "requestId": request_id
        }), 400

    return None


# ============================================================
# CONSULTAR PRODUTO
# GET /api/v1/products/{sku}
# ============================================================

@app.route("/api/v1/products/<sku>", methods=["GET"])
def get_product(sku):

    header_error = check_headers()

    if header_error:
        return header_error

    request_id = request.headers.get("X-Request-ID")

    response = None

    if sku not in PRODUCTS:

        response = jsonify({
            "code": "PRODUCT_NOT_FOUND",
            "message": "Product not found",
            "requestId": request_id
        })

        response.status_code = 404

    else:

        response = jsonify(PRODUCTS[sku])
        response.status_code = 200

    # O contrato exige devolver o X-Request-ID
    response.headers["X-Request-ID"] = request_id

    return response


# ============================================================
# CALCULAR COTAÇÃO
# POST /api/v1/quotes
# ============================================================

@app.route("/api/v1/quotes", methods=["POST"])
def create_quote():

    header_error = check_headers()

    if header_error:
        return header_error

    request_id = request.headers.get("X-Request-ID")

    data = request.get_json(silent=True)

    if not data or "items" not in data:

        response = jsonify({
            "code": "INVALID_REQUEST",
            "message": "Invalid request",
            "requestId": request_id
        })

        response.status_code = 400
        response.headers["X-Request-ID"] = request_id

        return response

    items = data["items"]

    # Deve possuir de 1 a 5 itens
    if not isinstance(items, list) or len(items) < 1 or len(items) > 5:

        response = jsonify({
            "code": "INVALID_QUANTITY_OR_ITEMS",
            "message": "Invalid number of items",
            "requestId": request_id
        })

        response.status_code = 422
        response.headers["X-Request-ID"] = request_id

        return response

    # Verificar SKUs duplicados
    skus = [item.get("sku") for item in items]

    if len(skus) != len(set(skus)):

        response = jsonify({
            "code": "INVALID_QUANTITY_OR_ITEMS",
            "message": "Duplicate SKU",
            "requestId": request_id
        })

        response.status_code = 422
        response.headers["X-Request-ID"] = request_id

        return response

    subtotal = 0

    for item in items:

        sku = item.get("sku")
        quantity = item.get("quantity")

        # Produto inexistente
        if sku not in PRODUCTS:

            response = jsonify({
                "code": "INVALID_PRODUCT",
                "message": "Invalid product",
                "requestId": request_id
            })

            response.status_code = 422
            response.headers["X-Request-ID"] = request_id

            return response

        # Quantidade inválida
        if (
            not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity < 1
            or quantity > 10
        ):

            response = jsonify({
                "code": "INVALID_QUANTITY_OR_ITEMS",
                "message": "Invalid quantity",
                "requestId": request_id
            })

            response.status_code = 422
            response.headers["X-Request-ID"] = request_id

            return response

        subtotal += PRODUCTS[sku]["unitPriceCents"] * quantity

    # ========================================================
    # DESCONTO
    # ========================================================

    if subtotal < 50000:
        discount_percent = 0

    elif subtotal < 100000:
        discount_percent = 5

    else:
        discount_percent = 10

    discount_cents = subtotal * discount_percent // 100

    total_cents = subtotal - discount_cents

    response = jsonify({
        "requestId": request_id,
        "subtotalCents": subtotal,
        "discountPercent": discount_percent,
        "discountCents": discount_cents,
        "totalCents": total_cents
    })

    response.status_code = 200
    response.headers["X-Request-ID"] = request_id

    return response


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CONECTASHOP - SERVIDOR REST DE TESTE")
    print("http://localhost:8080")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )