"""
WindDriver — live Venice wind for the Nabatele control system.

Single public API:
    Fetch() -> (tdu.Vector direction, float speed_m_s)

- Non-blocking curl transport; never raises into the cook.
- Returns last-good value until a fresh response lands.
- Direction vector points DOWNWIND (the way the structure is pushed),
  horizontal only: (x, 0, z). No vertical component by design.

Source note: station PWS_VENEZIA1 is disabled, so live observations are
empty and the ECMWF forecast block is used instead. Source() reports
'forecast' or 'live' so the UI can show which feed is driving Mode 2.
"""

import subprocess
import json
import math
import time

import tdu

BASE = "https://api.windyapp.co/v10/meteostations/getData"
STATION = "PWS_VENEZIA1"


class WindDriver:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._proc = None
        self._last_vec = tdu.Vector(0, 0, 0)
        self._last_speed = 0.0
        self._source = "none"  # 'live' | 'forecast' | 'none'

    # ---- public API ----

    def Fetch(self):
        """Non-blocking. Call at a low rate. Returns (direction, speed_m_s)."""
        if self._proc is not None:
            try:
                out, _ = self._proc.communicate(timeout=0)
                self._proc = None
                self._parse(out)
            except subprocess.TimeoutExpired:
                return self._last_vec, self._last_speed  # still in flight

        self._proc = subprocess.Popen(
            ["curl", "-s", "--max-time", "5", self._url()],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return self._last_vec, self._last_speed

    def Source(self):
        """'live', 'forecast', or 'none' — which feed last produced a value."""
        return self._source

    # ---- internals ----

    def _url(self):
        return (
            f"{BASE}/{STATION}"
            f"?key={self._api_key}"
            f"&predict=1&predictTemperature=1&canWindNull=1&info=1"
        )

    def _parse(self, raw: str):
        if not raw:
            return
        try:
            data = json.loads(raw)
            resp = data["response"]

            # Prefer real station observations if the station ever comes back.
            obs = resp.get("data") or []
            if obs:
                row = min(obs, key=lambda r: abs(r["timestamp"] - time.time()))
                source = "live"
            else:
                # Station disabled -> fall back to the ECMWF forecast block,
                # picking the hour nearest to now.
                rows = resp["predict"]["data"]
                if not rows:
                    return  # keep last good
                row = min(rows, key=lambda r: abs(r["timestamp"] - time.time()))
                source = "forecast"

            speed = float(row["wind_avg"])
            deg = float(row["wind_direction"])
        except (ValueError, KeyError, TypeError, IndexError):
            return  # keep last good

        # Meteorological deg = where wind comes FROM. Vector points downwind
        # (TOWARD), horizontal only — no Y component.
        rad = math.radians(deg)
        self._last_vec = tdu.Vector(-math.sin(rad), 0.0, -math.cos(rad))
        self._last_speed = speed
        self._source = source