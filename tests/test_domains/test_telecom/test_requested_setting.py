"""Offline checks for target-state requests, retries, and legacy replay."""

import pytest

from tau2.data_model.message import ToolCall
from tau2.domains.telecom.environment import get_environment
from tau2.domains.telecom.user_data_model import (
    SignalStrength,
    TelecomUserDB,
)
from tau2.domains.telecom.user_tools import TelecomUserTools


@pytest.fixture
def tools():
    return TelecomUserTools(TelecomUserDB())


@pytest.mark.parametrize(
    "name,field",
    [("toggle_roaming", "roaming_enabled"), ("toggle_wifi", "wifi_enabled")],
)
@pytest.mark.parametrize("initial", [False, True])
@pytest.mark.parametrize("target", [False, True])
def test_explicit_target_and_retry(tools, name, field, initial, target):
    setattr(tools.device, field, initial)
    tool = tools.get_tools()[name]
    tool(enabled=target)
    assert getattr(tools.device, field) is target
    after = tools.db.model_dump()
    result = tool(enabled=target)
    assert "unchanged" in result
    assert tools.db.model_dump() == after


@pytest.mark.parametrize("name", ["toggle_roaming", "toggle_wifi"])
def test_old_no_argument_and_null_calls_match_legacy_mutation(tools, name):
    reference = TelecomUserTools(tools.db.model_copy(deep=True))
    for kwargs in ({}, {"enabled": None}, {}):
        result = tools.get_tools()[name](**kwargs)
        new_state = getattr(reference, "_" + name)()
        label = "Data Roaming" if name == "toggle_roaming" else "Wi-Fi"
        assert result == (
            f"{label} is now {'ON' if new_state else 'OFF'}."
            f"\nStatus Bar: {reference._check_status_bar()}"
        )
        assert tools.db.model_dump() == reference.db.model_dump()


def test_keep_wifi_on_preserves_existing_connection(tools):
    tools.device.wifi_enabled = True
    tools.device.wifi_connected = True
    tools.device.wifi_ssid = "Existing network"
    tools.device.wifi_signal_strength = SignalStrength.GOOD
    before = tools.db.model_dump()
    tools.get_tools()["toggle_wifi"](enabled=True)
    assert tools.db.model_dump() == before


def test_turn_wifi_off_disconnects(tools):
    tools.device.wifi_enabled = True
    tools.device.wifi_connected = True
    tools.device.wifi_ssid = "Existing network"
    tools.device.wifi_signal_strength = SignalStrength.GOOD
    tools.get_tools()["toggle_wifi"](enabled=False)
    assert tools.device.wifi_enabled is False
    assert tools.device.wifi_connected is False
    assert tools.device.wifi_ssid is None
    assert tools.device.wifi_signal_strength == SignalStrength.NONE


def test_airplane_mode_still_blocks_wifi_change(tools):
    tools.device.airplane_mode = True
    tools.device.wifi_enabled = False
    before = tools.db.model_dump()
    result = tools.get_tools()["toggle_wifi"](enabled=True)
    assert "Cannot change" in result
    assert tools.db.model_dump() == before
    result = tools.get_tools()["toggle_wifi"](enabled=False)
    assert "unchanged" in result
    assert tools.db.model_dump() == before


def test_roaming_does_not_enable_provider_permission_or_other_settings(tools):
    tools.surroundings.is_abroad = True
    tools.surroundings.roaming_allowed = False
    tools.device.roaming_enabled = False
    tools.device.data_enabled = False
    tools.get_tools()["toggle_roaming"](enabled=True)
    assert tools.device.roaming_enabled is True
    assert tools.surroundings.roaming_allowed is False
    assert tools.device.data_enabled is False


@pytest.mark.parametrize("name", ["toggle_roaming", "toggle_wifi"])
def test_target_is_optional_in_model_tool_schema(tools, name):
    schema = tools.get_tools()[name].openai_schema["function"]["parameters"]
    assert "enabled" in schema["properties"]
    assert "enabled" not in schema.get("required", [])


@pytest.mark.parametrize(
    "name,field",
    [("toggle_roaming", "roaming_enabled"), ("toggle_wifi", "wifi_enabled")],
)
def test_requested_state_through_environment(name, field):
    environment = get_environment()
    setattr(environment.user_tools.device, field, True)
    for index in range(2):
        response = environment.get_response(
            ToolCall(
                id=f"requested-state-{index}",
                name=name,
                arguments={"enabled": False},
                requestor="user",
            )
        )
        assert not response.error
        assert getattr(environment.user_tools.device, field) is False
