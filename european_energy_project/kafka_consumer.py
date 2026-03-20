import json
import os
import sys
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaError
sys.path.insert(0, os.path.dirname(__file__))
from db_writer import init_db, insert_reading, log_pipeline_event

load_dotenv()

BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")
SSL_CA = os.getenv("KAFKA_SSL_CA", "certs/ca.pem")
SSL_CERT = os.getenv("KAFKA_SSL_CERT", "certs/service.cert")
SSL_KEY = os.getenv("KAFKA_SSL_KEY", "certs/service.key")
TOPIC = os.getenv("KAFKA_TOPIC", "energy-readings")


def build_consumer() -> Consumer:
    return Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVER,
        "security.protocol": "SSL",
        "ssl.ca.location": SSL_CA,
        "ssl.certificate.location": SSL_CERT,
        "ssl.key.location": SSL_KEY,
        "group.id": "energyops-dashboard-consumer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })


def run_consumer():
    init_db()
    consumer = build_consumer()
    consumer.subscribe([TOPIC])
    log_pipeline_event("CONSUMER_START", f"Subscribed to topic: {TOPIC}")
    print(f"[CONSUMER] Listening on {TOPIC}...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"[CONSUMER] Error: {msg.error()}")
                log_pipeline_event("CONSUMER_ERROR", str(msg.error()))
                continue

            try:
                reading = json.loads(msg.value().decode("utf-8"))
                insert_reading(reading)
                log_pipeline_event(
                    "MESSAGE_CONSUMED",
                    f"Site: {reading.get('site')} | "
                    f"Consumption: {reading.get('consumption_kw')}kW | "
                    f"Anomaly: {reading.get('anomaly')}"
                )
                print(f"[CONSUMER] Stored: {reading.get('site')} — {reading.get('consumption_kw')}kW")
            except Exception as e:
                print(f"[CONSUMER] Parse error: {e}")
                log_pipeline_event("PARSE_ERROR", str(e))

    except KeyboardInterrupt:
        print("[CONSUMER] Shutting down")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
