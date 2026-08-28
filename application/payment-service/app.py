from flask import Flask, jsonify
import logging
import os
import socket
import time
from datetime import datetime, timezone

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

logger = logging.getLogger("payment-service")


@app.route("/")
def home():
    logger.info("Payment service request received")

    return jsonify({
        "service": "payment-service",
        "status": "UP",
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "payment-service",
        "status": "healthy"
    }), 200


@app.route("/payments/<payment_id>")
def get_payment(payment_id):
    logger.info("Processing payment: %s", payment_id)

    return jsonify({
        "payment_id": payment_id,
        "order_id": "ORD-1001",
        "amount": 75000,
        "currency": "INR",
        "status": "SUCCESS"
    })


@app.route("/payments/slow")
def slow_payment():
    logger.warning("Simulating slow payment processing")

    time.sleep(5)

    return jsonify({
        "payment_id": "PAY-SLOW-001",
        "status": "SUCCESS",
        "message": "Payment completed after simulated delay"
    })


@app.route("/payments/failure")
def payment_failure():
    logger.error("Simulated payment processing failure")

    return jsonify({
        "payment_id": "PAY-FAIL-001",
        "status": "FAILED",
        "message": "Simulated payment gateway failure"
    }), 500


@app.route("/error")
def generate_error():
    logger.error("Simulated payment-service application error")

    return jsonify({
        "service": "payment-service",
        "error": "Simulated payment failure"
    }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5002"))
    )