"""Read the odometer from the Alfa Connect (Uconnect) cloud and append it to docs/readings.json.

Environment variables:
  UCONNECT_EMAIL     your Alfa Connect login e-mail      (required)
  UCONNECT_PASSWORD  your Alfa Connect password          (required)
  UCONNECT_BRAND     brand/region config, default ALFA_ROMEO_EU
                     other options: ALFA_ROMEO_US_CANADA, ALFA_ROMEO_ASIA
  UCONNECT_VIN       only needed if the account has more than one car
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "docs" / "readings.json"
MILES_TO_KM = 1.609344


def to_km(value, unit):
    """Convert the odometer value to whole kilometres."""
    unit_text = str(unit or "km").lower()
    if "mi" in unit_text and "km" not in unit_text:
        value = value * MILES_TO_KM
    return int(round(float(value)))


def add_reading(data, date, odo):
    """Insert or replace today's reading. Returns a message describing what happened."""
    readings = data.setdefault("readings", [])
    earlier = [r for r in readings if r["date"] < date]
    if earlier and odo < earlier[-1]["odo"]:
        return f"Skipped: {odo} km is lower than the previous reading ({earlier[-1]['odo']} km)."
    readings[:] = [r for r in readings if r["date"] != date]
    readings.append({"date": date, "odo": odo})
    readings.sort(key=lambda r: r["date"])
    data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"Saved {odo} km for {date}."


async def fetch_odometer():
    from py_uconnect import Client, brands

    email = os.environ["UCONNECT_EMAIL"]
    password = os.environ["UCONNECT_PASSWORD"]
    brand_name = os.environ.get("UCONNECT_BRAND", "ALFA_ROMEO_EU")
    brand = getattr(brands, brand_name)

    async with Client(email, password, pin=None, brand=brand) as client:
        vehicles = await client.refresh()
        if not vehicles:
            raise SystemExit("Login worked but no vehicles were found on this account.")

        wanted = os.environ.get("UCONNECT_VIN")
        if wanted:
            vehicle = vehicles[wanted]
        else:
            vehicle = next(iter(vehicles.values()))
            if len(vehicles) > 1:
                print("Several vehicles found, using the first. Set UCONNECT_VIN to choose:")
                for vin, v in vehicles.items():
                    print(f"  {vin}  {v.make} {v.model}")

        unit = getattr(vehicle, "odometer_unit", None)
        print(f"Vehicle: {vehicle.make} {vehicle.model}, odometer={vehicle.odometer} {unit or ''}")
        if vehicle.odometer is None:
            return None
        return to_km(vehicle.odometer, unit)


def main():
    odo = asyncio.run(fetch_odometer())
    if odo is None:
        print("The car did not report an odometer value. Nothing saved.")
        return 0

    data = json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else {}
    today = datetime.now(timezone.utc).date().isoformat()
    print(add_reading(data, today, odo))
    DATA_FILE.write_text(json.dumps(data, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
