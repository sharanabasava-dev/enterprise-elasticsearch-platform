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

@app.route("/customer-orders/<customer_id>")
def get_customer_orders(customer_id):
    logger.info("Fetching order information for customer: %s", customer_id)

    order_service_url = os.getenv(
        "ORDER_SERVICE_URL",
        "http://order-service:5001"
    )

    try:
        response = requests.get(
            f"{order_service_url}/orders/ORD-1001",
            timeout=5
        )

        response.raise_for_status()

        order_data = response.json()

        return jsonify({
            "customer_id": customer_id,
            "customer_status": "active",
            "order": order_data
        })

    except requests.RequestException as error:
        logger.error(
            "Failed to communicate with order-service: %s",
            error
        )

        return jsonify({
            "error": "Order service unavailable"
        }), 503
        
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )