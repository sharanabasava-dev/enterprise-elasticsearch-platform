import requests
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

@app.route("/orders/<order_id>/checkout")
def checkout_order(order_id):
    logger.info("Starting checkout for order: %s", order_id)

    payment_service_url = os.getenv(
        "PAYMENT_SERVICE_URL",
        "http://payment-service:5002"
    )

    try:
        response = requests.get(
            f"{payment_service_url}/payments/PAY-1001",
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
            "payment": payment_data
        })

    except requests.RequestException as error:
        logger.error(
            "Payment service communication failed: %s",
            error
        )

        return jsonify({
            "order_id": order_id,
            "order_status": "PAYMENT_FAILED",
            "error": "Payment service unavailable"
        }), 503
        
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5001"))
    )