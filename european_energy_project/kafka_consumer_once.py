import json
import os
import sys
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaError

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.insert(0, os.path.dirname(__file__))
from db_writer import init_db, insert_reading, log_pipeline_event

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
        "group.id": "energyops-github-actions",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })


def run_once():
    """
    Consume all pending messages from Kafka topic and write to SQLite.
    Exits after 10 seconds of no new messages.
    """
    init_db()
    consumer = build_consumer()
    consumer.subscribe([TOPIC])
    log_pipeline_event("GITHUB_ACTIONS_RUN", "One-shot consumer started")
    print(f"[CONSUMER] Consuming from {TOPIC}...")

    messages_consumed = 0
    empty_polls = 0
    max_empty_polls = 5

    try:
        while empty_polls < max_empty_polls:
            msg = consumer.poll(timeout=2.0)
            if msg is None:
                empty_polls += 1
                print(f"[CONSUMER] No message ({empty_polls}/{max_empty_polls} empty polls)")
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    empty_polls += 1
                    continue
                print(f"[CONSUMER] Error: {msg.error()}")
                continue

            empty_polls = 0
            try:
                reading = json.loads(msg.value().decode("utf-8"))
                insert_reading(reading)
                messages_consumed += 1
                log_pipeline_event(
                    "MESSAGE_CONSUMED",
                    f"Site: {reading.get('site')} | "
                    f"Consumption: {reading.get('consumption_kw')}kW"
                )
                print(
                    f"[CONSUMER] Stored: {reading.get('site')} — "
                    f"{reading.get('consumption_kw')}kW"
                )
            except Exception as e:
                print(f"[CONSUMER] Parse error: {e}")
                log_pipeline_event("PARSE_ERROR", str(e))

    finally:
        consumer.close()
        print(f"[CONSUMER] Done — {messages_consumed} messages consumed.")


if __name__ == "__main__":
    run_once()
