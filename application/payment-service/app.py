from flask import Flask, jsonify, request, has_request_context
import logging
import os
import socket
import time
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

for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIdFilter())


logger = logging.getLogger("payment-service")


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
    logger.info("Payment service request received")

    return jsonify({
        "service": "payment-service",
        "status": "UP",
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request.request_id
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "payment-service",
        "status": "healthy",
        "request_id": request.request_id
    }), 200


@app.route("/payments/<payment_id>")
def get_payment(payment_id):
    logger.info(
        "Processing payment: %s",
        payment_id
    )

    return jsonify({
        "payment_id": payment_id,
        "order_id": "ORD-1001",
        "amount": 75000,
        "currency": "INR",
        "status": "SUCCESS",
        "request_id": request.request_id
    })


@app.route("/payments/slow")
def slow_payment():
    logger.warning(
        "Simulating slow payment processing"
    )

    time.sleep(5)

    return jsonify({
        "payment_id": "PAY-SLOW-001",
        "status": "SUCCESS",
        "message": "Payment completed after simulated delay",
        "request_id": request.request_id
    })


@app.route("/payments/failure")
def payment_failure():
    logger.error(
        "Simulated payment processing failure"
    )

    return jsonify({
        "payment_id": "PAY-FAIL-001",
        "status": "FAILED",
        "message": "Simulated payment gateway failure",
        "request_id": request.request_id
    }), 500


@app.route("/error")
def generate_error():
    logger.error(
        "Simulated payment-service application error"
    )

    return jsonify({
        "service": "payment-service",
        "error": "Simulated payment failure",
        "request_id": request.request_id
    }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5002"))
    )