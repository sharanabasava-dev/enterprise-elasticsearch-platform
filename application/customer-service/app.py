from flask import Flask, jsonify
import logging
import os
import socket
from datetime import datetime, timezone

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

logger = logging.getLogger("customer-service")


@app.route("/")
def home():
    logger.info("Customer service request received")

    return jsonify({
        "service": "customer-service",
        "status": "UP",
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "customer-service",
        "status": "healthy"
    }), 200


@app.route("/customers/<customer_id>")
def get_customer(customer_id):
    logger.info("Fetching customer: %s", customer_id)

    return jsonify({
        "customer_id": customer_id,
        "name": f"Customer-{customer_id}",
        "status": "active"
    })


@app.route("/error")
def generate_error():
    logger.error("Simulated application error")

    return jsonify({
        "service": "customer-service",
        "error": "Simulated application failure"
    }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )