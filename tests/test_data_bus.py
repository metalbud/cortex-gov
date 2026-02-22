from pathlib import Path

from tools.system.data_bus import DataBus


def test_data_bus_event_and_data(tmp_path: Path):
    bus_path = tmp_path / "bus.json"
    bus = DataBus(bus_path=str(bus_path))

    event = bus.publish_event("integration_check", {"status": "ok"}, source="test")
    assert event["name"] == "integration_check"

    events = bus.get_events("integration_check")
    assert len(events) == 1

    bus.set_data("last_status", {"status": "ok"}, source="test")
    data = bus.get_data("last_status")
    assert data["value"]["status"] == "ok"
