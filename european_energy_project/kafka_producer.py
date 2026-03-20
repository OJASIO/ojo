import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from confluent_kafka import Producer
from energy_fetcher import fetch_all_sites

load_dotenv()

BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")
SSL_CA = os.getenv("KAFKA_SSL_CA", "certs/ca.pem")
SSL_CERT = os.getenv("KAFKA_SSL_CERT", "certs/service.cert")
SSL_KEY = os.getenv("KAFKA_SSL_KEY", "certs/service.key")
TOPIC = os.getenv("KAFKA_TOPIC", "energy-readings")
PUBLISH_INTERVAL_SECONDS = 120  # every 5 minutes


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


def publish_readings(producer: Producer):
    readings = fetch_all_sites()
    for reading in readings:
        producer.produce(
            topic=TOPIC,
            key=reading["site"].encode("utf-8"),
            value=json.dumps(reading).encode("utf-8"),
            callback=delivery_report,
        )
    producer.flush()
    print(f"[PRODUCER] Published {len(readings)} readings at {datetime.utcnow().isoformat()}")


def run_producer():
    print(f"[PRODUCER] Starting — publishing to {TOPIC} every {PUBLISH_INTERVAL_SECONDS}s")
    producer = build_producer()
    while True:
        try:
            publish_readings(producer)
        except Exception as e:
            print(f"[PRODUCER] Error: {e}")
        time.sleep(PUBLISH_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_producer()
