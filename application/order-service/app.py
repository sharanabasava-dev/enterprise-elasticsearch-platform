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

logger = logging.getLogger("order-service")


@app.route("/")
def home():
    logger.info("Order service request received")

    return jsonify({
        "service": "order-service",
        "status": "UP",
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "order-service",
        "status": "healthy"
    }), 200


@app.route("/orders/<order_id>")
def get_order(order_id):
    logger.info("Fetching order: %s", order_id)

    return jsonify({
        "order_id": order_id,
        "customer_id": "101",
        "product": "Laptop",
        "amount": 75000,
        "status": "confirmed"
    })


@app.route("/error")
def generate_error():
    logger.error("Simulated order-service failure")

    return jsonify({
        "service": "order-service",
        "error": "Simulated order processing failure"
    }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5001"))
    )