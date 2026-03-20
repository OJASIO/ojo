import json
import os
import sys
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.insert(0, os.path.dirname(__file__))
from energy_fetcher import fetch_all_sites

BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")
SSL_CA = os.getenv("KAFKA_SSL_CA", "certs/ca.pem")
SSL_CERT = os.getenv("KAFKA_SSL_CERT", "certs/service.cert")
SSL_KEY = os.getenv("KAFKA_SSL_KEY", "certs/service.key")
TOPIC = os.getenv("KAFKA_TOPIC", "energy-readings")


def build_producer() -> Producer:
    return Producer({
        "bootstrap.servers": BOOTSTRAP_SERVER,
        "security.protocol": "SSL",
        "ssl.ca.location": SSL_CA,
        "ssl.certificate.location": SSL_CERT,
        "ssl.key.location": SSL_KEY,
    })


def delivery_report(err, msg):
    if err:
        print(f"[PRODUCER] Delivery failed: {err}")
    else:
        print(f"[PRODUCER] Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


def run_once():
    """Fetch readings for all sites and publish to Kafka — runs once then exits."""
    print("[PRODUCER] Starting one-shot run...")
    producer = build_producer()
    readings = fetch_all_sites()
    for reading in readings:
        producer.produce(
            topic=TOPIC,
            key=reading["site"].encode("utf-8"),
            value=json.dumps(reading).encode("utf-8"),
            callback=delivery_report,
        )
    producer.flush()
    print(f"[PRODUCER] Published {len(readings)} readings — done.")


if __name__ == "__main__":
    run_once()
