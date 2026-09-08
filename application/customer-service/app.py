from flask import Flask, jsonify, request
import logging
import os
import socket
import uuid
from datetime import datetime, timezone

import requests

app = Flask(__name__)

logger = logging.getLogger("customer-service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s "
        "request_id=%(request_id)s message=%(message)s"
    )
)

if not logger.handlers:
    logger.addHandler(handler)

logger.propagate = False

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL",
    "http://order-service:5001"
)


@app.before_request
def add_request_id():
    request.request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4())
    )


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = getattr(
                request,
                "request_id",
                "unknown"
            )
        return True


for handler in logger.handlers:
    handler.addFilter(RequestContextFilter())


@app.after_request
def add_response_headers(response):
    response.headers["X-Request-ID"] = request.request_id
    return response


@app.route("/")
def home():
    logger.info(
        "Customer service request received",
        extra={"request_id": request.request_id}
    )

    return jsonify({
        "service": "customer-service",
        "status": "UP",
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/customers/<customer_id>")
def get_customer(customer_id):
    logger.info(
        f"Fetching customer: {customer_id}",
        extra={"request_id": request.request_id}
    )

    return jsonify({
        "customer_id": customer_id,
        "name": f"Customer-{customer_id}",
        "status": "active"
    })


@app.route("/error")
def error():
    logger.error(
        "Simulated customer service error",
        extra={"request_id": request.request_id}
    )

    return jsonify({
        "error": "simulated customer service failure"
    }), 500


@app.route("/customer-orders/<customer_id>")
def get_customer_orders(customer_id):
    logger.info(
        f"Fetching order information for customer: {customer_id}",
        extra={"request_id": request.request_id}
    )

    try:
        url = f"{ORDER_SERVICE_URL}/orders/ORD-1001"

        response = requests.get(
            url,
            headers={
                "X-Request-ID": request.request_id
            },
            timeout=5
        )

        response.raise_for_status()

        return jsonify({
            "customer_id": customer_id,
            "customer_status": "active",
            "order": response.json()
        })

    except requests.RequestException as exc:
        logger.error(
            f"Failed to fetch order information: {exc}",
            extra={"request_id": request.request_id}
        )

        return jsonify({
            "error": "order service unavailable"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)