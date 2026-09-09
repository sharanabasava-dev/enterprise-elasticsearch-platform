import requests
from flask import Flask, jsonify, request, has_request_context
import logging
import os
import socket
import uuid
from datetime import datetime, timezone

app = Flask(__name__)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(
                request,
                "request_id",
                "-"
            )
        else:
            record.request_id = "-"

        return True


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s "
           "request_id=%(request_id)s %(message)s"
)

# Make sure every log record has request_id,
# including logs generated outside a request context.
for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIdFilter())

logger = logging.getLogger("order-service")


@app.before_request
def add_request_id():
    request.request_id = request.headers.get(
        "X-Request-ID"
    ) or str(uuid.uuid4())


@app.after_request
def add_request_id_header(response):
    response.headers["X-Request-ID"] = request.request_id
    return response


@app.route("/")
def home():
    logger.info("Order service request received")

    return jsonify({
        "service": "order-service",
        "status": "UP",
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request.request_id
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "order-service",
        "status": "healthy",
        "request_id": request.request_id
    }), 200


@app.route("/orders/<order_id>")
def get_order(order_id):
    logger.info(
        "Fetching order: %s",
        order_id
    )

    return jsonify({
        "order_id": order_id,
        "customer_id": "101",
        "product": "Laptop",
        "amount": 75000,
        "status": "confirmed",
        "request_id": request.request_id
    })


@app.route("/error")
def generate_error():
    logger.error(
        "Simulated order-service failure"
    )

    return jsonify({
        "service": "order-service",
        "error": "Simulated order processing failure",
        "request_id": request.request_id
    }), 500


@app.route("/orders/<order_id>/checkout")
def checkout_order(order_id):
    logger.info(
        "Starting checkout for order: %s",
        order_id
    )

    payment_service_url = os.getenv(
        "PAYMENT_SERVICE_URL",
        "http://payment-service:5002"
    )

    try:
        response = requests.get(
            f"{payment_service_url}/payments/PAY-1001",
            headers={
                "X-Request-ID": request.request_id
            },
            timeout=5
        )

        response.raise_for_status()

        payment_data = response.json()

        logger.info(
            "Payment completed successfully for order: %s",
            order_id
        )

        return jsonify({
            "order_id": order_id,
            "order_status": "CONFIRMED",
            "payment": payment_data,
            "request_id": request.request_id
        })

    except requests.RequestException as error:
        logger.error(
            "Payment service communication failed: %s",
            error
        )

        return jsonify({
            "order_id": order_id,
            "order_status": "PAYMENT_FAILED",
            "error": "Payment service unavailable",
            "request_id": request.request_id
        }), 503


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5001"))
    )