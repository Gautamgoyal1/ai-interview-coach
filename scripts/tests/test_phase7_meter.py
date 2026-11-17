"""Budget checks happen before transport; no provider calls in these tests."""

import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

spec = importlib.util.spec_from_file_location("phase7_meter", Path(__file__).parents[1] / "phase7_meter.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_budget_stop_precedes_a_transport_call(tmp_path):
    meter = module.Meter(tmp_path)
    meter.reserve("test", "test", 1.99)
    create = AsyncMock()
    provider = SimpleNamespace(client=SimpleNamespace(responses=SimpleNamespace(create=create)))
    meter.observe_azure(provider)
    with pytest.raises(module.BudgetStop):
        asyncio.run(provider.client.responses.create(model="gpt-5.4-mini", max_output_tokens=4000, input="test"))
    create.assert_not_called()
    assert len(meter.ledger["requests"]) == 1


def test_failure_keeps_reservation_across_restart(tmp_path):
    meter = module.Meter(tmp_path)
    create = AsyncMock(side_effect=RuntimeError("transport unavailable"))
    provider = SimpleNamespace(client=SimpleNamespace(responses=SimpleNamespace(create=create)))
    meter.observe_azure(provider)
    with pytest.raises(RuntimeError):
        asyncio.run(provider.client.responses.create(model="gpt-5.4-mini", max_output_tokens=4000, input="test"))
    record = module.Meter(tmp_path).ledger["requests"][0]
    assert record["status"] == "FAILED" and record["budget_charge_usd"] > 0
    assert create.await_count == 1


def test_known_usage_replaces_reservation_with_conservative_charge(tmp_path):
    meter = module.Meter(tmp_path)
    response = SimpleNamespace(model_dump=lambda **_: dict(usage=dict(input_tokens=100, output_tokens=50), model="gpt-5.4-mini", status="completed"))
    provider = SimpleNamespace(client=SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(return_value=response))))
    meter.observe_azure(provider)
    asyncio.run(provider.client.responses.create(model="gpt-5.4-mini", max_output_tokens=4000, input="test"))
    record = meter.ledger["requests"][0]
    assert record["budget_charge_usd"] == pytest.approx(.0015)
    assert record["reference_cost_usd"] == pytest.approx(.0003)
