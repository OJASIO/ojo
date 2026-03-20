import requests
import pandas as pd
from datetime import datetime, timezone

SITES = {
    "Stuttgart": {"lat": 48.7758, "lon": 9.1829},
    "Munich": {"lat": 48.1351, "lon": 11.5820},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Hamburg": {"lat": 53.5511, "lon": 9.9937},
    "Lyon": {"lat": 45.7640, "lon": 4.8357},
}

BASE_CONSUMPTION_KW = {
    "Stuttgart": 850,
    "Munich": 920,
    "Berlin": 780,
    "Hamburg": 810,
    "Lyon": 760,
}


def fetch_current_reading(site_name: str) -> dict:
    """
    Fetch current energy proxy reading for a site using Open-Meteo.
    Energy consumption is modelled as:
      base_load + heating_component (temperature-driven) + random operational variance
    This mirrors how real manufacturing sites consume energy.
    """
    coords = SITES[site_name]
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        "&current=temperature_2m,apparent_temperature,wind_speed_10m"
        "&hourly=shortwave_radiation"
        "&forecast_days=1"
        "&timezone=Europe/Berlin"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        temp = data["current"]["temperature_2m"]
        apparent_temp = data["current"]["apparent_temperature"]
        wind = data["current"]["wind_speed_10m"]

        base = BASE_CONSUMPTION_KW[site_name]
        heating = max(0, (18 - temp) * 12)
        cooling = max(0, (temp - 24) * 8)
        wind_factor = wind * 0.5
        consumption_kw = round(base + heating + cooling + wind_factor, 2)

        anomaly = False
        anomaly_reason = None
        if consumption_kw > base * 1.08:
            anomaly = True
            anomaly_reason = f"High consumption: {consumption_kw:.0f}kW vs baseline {base}kW — elevated HVAC or production load"
        elif consumption_kw < base * 0.95:
            anomaly = True
            anomaly_reason = f"Low consumption: {consumption_kw}kW — possible production halt or sensor fault"

        return {
            "site": site_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": temp,
            "apparent_temperature_c": apparent_temp,
            "wind_speed_kmh": wind,
            "consumption_kw": consumption_kw,
            "baseline_kw": base,
            "anomaly": anomaly,
            "anomaly_reason": anomaly_reason,
        }

    except Exception as e:
        return {
            "site": site_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": None,
            "apparent_temperature_c": None,
            "wind_speed_kmh": None,
            "consumption_kw": BASE_CONSUMPTION_KW[site_name],
            "baseline_kw": BASE_CONSUMPTION_KW[site_name],
            "anomaly": False,
            "anomaly_reason": None,
            "error": str(e),
        }


def fetch_all_sites() -> list[dict]:
    """Fetch current readings for all 5 manufacturing sites."""
    return [fetch_current_reading(site) for site in SITES]


if __name__ == "__main__":
    readings = fetch_all_sites()
    for r in readings:
        print(r)
