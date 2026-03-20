# ⚡ EnergyOps Assistant

A production-grade real-time energy monitoring platform for global manufacturing sites,
built with Apache Kafka, Python, SQLite, and Groq LLaMA 3.

## Architecture

```
Open-Meteo API (real weather/energy data)
        ↓
[Kafka Producer] — publishes to Aiven Apache Kafka every 5 minutes
        ↓  SSL/TLS encrypted
Aiven Apache Kafka 4.1 (Topic: energy-readings, Europe region)
        ↓
[Kafka Consumer] — consumes messages, writes to SQLite
        ↓
SQLite Database (energy.db) — raw_readings | anomaly_flags | pipeline_logs
        ↓
[Streamlit App] — 3-tab dashboard
  ├── Operations Dashboard (Plotly charts, anomaly alerts)
  ├── AI Knowledge Assistant (Groq LLaMA 3 + data context injection)
  └── Pipeline Monitor (job status, logs, data volume)
```

## Features

- **Real-time Kafka streaming** — energy readings published every 5 minutes from 5 European manufacturing sites
- **Anomaly detection** — Z-score based consumption spike detection with automated alerting
- **GenAI chatbot** — Ask questions about energy data in natural language; LLM receives live data as context
- **Automated reporting** — AI-generated weekly platform transparency reports (Markdown export)
- **Pipeline monitoring** — Full visibility into Kafka consumer health and message processing

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Streaming | Apache Kafka 4.1 (Aiven managed, Europe region) |
| Data source | Open-Meteo API (real European weather/energy data) |
| Storage | SQLite |
| AI | Groq LLaMA 3 (llama3-8b-8192) |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.11 |

## Local Setup

```bash
# 1. Clone and install
git clone https://github.com/yourusername/energyops-assistant
cd energyops-assistant
pip install -r requirements.txt

# 2. Add certificates
# Download from Aiven console → Service settings → Connection information
# Place in certs/ folder:
#   certs/ca.pem
#   certs/service.cert
#   certs/service.key

# 3. Configure environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# 4. Initialise database
python consumer/db_writer.py

# 5. Start producer (Terminal 1)
cd producer && python kafka_producer.py

# 6. Start consumer (Terminal 2)
cd consumer && python kafka_consumer.py

# 7. Launch dashboard (Terminal 3)
cd app && streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push to GitHub (certs/ and .env are gitignored)
2. Go to share.streamlit.io → New app → select repo
3. Add secrets in Streamlit Cloud dashboard:
   - `GROQ_API_KEY`
   - `KAFKA_BOOTSTRAP_SERVER`
   - `KAFKA_CA_CERT` (paste full ca.pem contents)
   - `KAFKA_ACCESS_CERT` (paste full service.cert contents)
   - `KAFKA_ACCESS_KEY` (paste full service.key contents)
4. Commit `energy.db` to repo (pre-populated with initial data)

## Project Context

Built as a portfolio project targeting Bosch's Digital Platform Operations internship.
Demonstrates: Kafka streaming pipelines, real-time data monitoring, GenAI integration,
and operational dashboard development — directly mapping to the role requirements.

The architecture mirrors production patterns used at enterprise scale:
separation of ingestion (producer), transformation (consumer), storage (SQLite),
and serving (Streamlit) layers — the same pattern used in regulated financial
data pipelines at Yubi and Teradata.
