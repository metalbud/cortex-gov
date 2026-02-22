#!/usr/bin/env python3
"""
Cross-tool communication and data sharing for Cortex GOV.
Provides a simple JSON-backed event and data bus for tools to publish/consume.
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataBus:
    """JSON-backed data bus for cross-tool communication."""

    def __init__(self, bus_path: str = "artifacts/system-analysis/data-bus.json"):
        self.bus_path = Path(bus_path)
        self.bus_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_bus()

    def _ensure_bus(self):
        if not self.bus_path.exists():
            self._write_bus({"version": "1.0", "events": [], "data": {}})

    def _read_bus(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(self.bus_path.read_text(encoding="utf-8"))

    def _write_bus(self, payload: Dict[str, Any]):
        with self._lock:
            self.bus_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def publish_event(self, name: str, payload: Dict[str, Any], source: str = "unknown") -> Dict[str, Any]:
        """Publish an event to the bus."""
        bus = self._read_bus()
        event = {
            "id": f"evt_{int(time.time()*1000)}",
            "name": name,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }
        bus["events"].append(event)
        self._write_bus(bus)
        return event

    def get_events(self, name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent events, optionally filtered by name."""
        bus = self._read_bus()
        events = bus.get("events", [])
        if name:
            events = [evt for evt in events if evt.get("name") == name]
        return events[-limit:]

    def set_data(self, key: str, value: Any, source: str = "unknown") -> Dict[str, Any]:
        """Set shared data in the bus."""
        bus = self._read_bus()
        bus["data"][key] = {
            "value": value,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self._write_bus(bus)
        return bus["data"][key]

    def get_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Get shared data by key."""
        bus = self._read_bus()
        return bus.get("data", {}).get(key)

    def clear_events(self):
        """Clear all events (useful for testing)."""
        bus = self._read_bus()
        bus["events"] = []
        self._write_bus(bus)


if __name__ == "__main__":
    bus = DataBus()
    event = bus.publish_event("integration_check", {"status": "ok"}, source="integration_checker")
    print(f"Published event: {event['id']}")
    bus.set_data("latest_integration_report", {"status": "good"}, source="integration_checker")
    print("Latest integration report:", bus.get_data("latest_integration_report"))
