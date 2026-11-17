"""Local audit-only API metering. Reserve pessimistic cost before sending.

The ledger is resumable; failures retain the full reservation. These are local
estimates, not Azure account billing or an enforceable provider spending cap.
"""

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx


class BudgetStop(BaseException):
    """Must not be swallowed by production fallbacks."""


class Meter:
    def __init__(self, output: Path, guard_rates: dict | None = None):
        self.output = output
        output.mkdir(parents=True, exist_ok=True)
        self.path = output / "api-usage.json"
        self.active_case = None
        self.ledger = (
            json.loads(self.path.read_text())
            if self.path.exists()
            else {
                "limit_usd": 2,
                "requests": [],
                "actual_billed_charge_usd": None,
                "reference_rates_per_million": {
                    "azure_input": 0.75,
                    "azure_output": 4.5,
                    "gemini_input": 0.15,
                },
                "guard_rates_per_million": {
                    "azure_input": 5,
                    "azure_output": 20,
                    "gemini_input": 1,
                },
                "pricing_checked_on": "2026-11-16",
            }
        )
        if guard_rates is not None:
            if self.path.exists():
                assert (
                    self.ledger["guard_rates_per_million"] == guard_rates
                ), "Do not change a running task's budget rates"
            else:
                self.ledger["guard_rates_per_million"] = guard_rates

    def save(self):
        self.ledger["conservative_budget_charge_usd"] = sum(
            r["budget_charge_usd"] for r in self.ledger["requests"]
        )
        self.ledger["reference_estimated_cost_usd"] = sum(
            r.get("reference_cost_usd", 0) for r in self.ledger["requests"]
        )
        self.path.write_text(json.dumps(self.ledger, indent=2) + "\n")

    def reserve(self, provider, model, amount, **extra):
        if sum(r["budget_charge_usd"] for r in self.ledger["requests"]) + amount > 2:
            raise BudgetStop("$2 conservative reservation exhausted; request NOT sent")
        record = dict(
            id=len(self.ledger["requests"]) + 1,
            provider=provider,
            model=model,
            case_id=self.active_case,
            status="RESERVED",
            budget_charge_usd=amount,
            started_at_utc=datetime.now(timezone.utc).isoformat(),
            **extra,
        )
        self.ledger["requests"].append(record)
        self.save()
        return record

    def write(self, kind, record, data):
        (self.output / f'{kind}-{record["id"]:03d}.json').write_text(
            json.dumps(data, indent=2) + "\n"
        )

    def observe_azure(self, provider):
        original = provider.client.responses.create

        async def create(**kwargs):
            assert (
                kwargs["model"] == "gpt-5.4-mini"
                and kwargs["max_output_tokens"] == 4000
            )
            assert not kwargs.get("tools")
            upper = (
                len(kwargs["input"].encode())
                + len((kwargs.get("instructions") or "").encode())
                + 1024
            )
            rates = self.ledger["guard_rates_per_million"]
            task = (
                "semantic_screen"
                if "draft interview QUESTION" in (kwargs.get("instructions") or "")
                else "question_generation"
            )
            r = self.reserve(
                "azure_openai",
                kwargs["model"],
                (upper * rates["azure_input"] + 4000 * rates["azure_output"]) / 1e6,
                task=task,
                input_token_upper_bound=upper,
                max_output_tokens=4000,
            )
            self.write("request", r, kwargs)
            started = time.perf_counter()
            try:
                response = await original(**kwargs)
                data = response.model_dump(mode="json")
                r.update(
                    status="SUCCEEDED",
                    usage=data.get("usage"),
                    response_model=data.get("model"),
                    response_status=data.get("status"),
                )
                usage = data.get("usage") or {}
                if isinstance(usage.get("input_tokens"), int) and isinstance(
                    usage.get("output_tokens"), int
                ):
                    i, o = usage["input_tokens"], usage["output_tokens"]
                    r.update(
                        budget_charge_usd=(
                            i * rates["azure_input"] + o * rates["azure_output"]
                        )
                        / 1e6,
                        reference_cost_usd=(i * 0.75 + o * 4.5) / 1e6,
                    )
                self.write("response", r, data)
                return response
            except BaseException as error:
                r.update(status="FAILED", error_type=type(error).__name__)
                raise
            finally:
                r["elapsed_seconds"] = time.perf_counter() - started
                self.save()

        provider.client.responses.create = create

    def observe_gemini(self):
        original = httpx.AsyncClient.post

        async def post(client, url, *args, **kwargs):
            if not str(url).startswith("https://generativelanguage.googleapis.com/"):
                return await original(client, url, *args, **kwargs)
            body = kwargs["json"]
            counting = str(url).endswith(":countTokens")
            assert counting or str(url).endswith(
                "/gemini-embedding-001:batchEmbedContents"
            )
            if counting:
                texts = [p["text"] for c in body["contents"] for p in c["parts"]]
            else:
                assert all(
                    p["outputDimensionality"] == 768
                    and p["taskType"] in {"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}
                    for p in body["requests"]
                )
                texts = [p["content"]["parts"][0]["text"] for p in body["requests"]]
            upper = sum(len(t.encode()) + 32 for t in texts)
            r = self.reserve(
                "gemini",
                "gemini-embedding-001",
                (
                    0
                    if counting
                    else upper
                    * self.ledger["guard_rates_per_million"]["gemini_input"]
                    / 1e6
                ),
                task="token_count" if counting else "embedding",
                inputs=len(texts),
                task_types=(
                    [] if counting else [p["taskType"] for p in body["requests"]]
                ),
                estimated_input_tokens_chars_div_4=sum(map(len, texts)) / 4,
                input_hashes=[hashlib.sha256(t.encode()).hexdigest() for t in texts],
            )
            self.write("request", r, body)
            started = time.perf_counter()
            try:
                response = await original(client, url, *args, **kwargs)
                r["http_status"] = response.status_code
                if response.status_code == 200:
                    data = response.json()
                    if not counting:
                        assert len(data["embeddings"]) == len(texts)
                        assert all(
                            len(e["values"]) == 768
                            and all(math.isfinite(x) for x in e["values"])
                            and any(e["values"])
                            for e in data["embeddings"]
                        )
                    r.update(
                        status="SUCCEEDED",
                        reference_cost_usd=(
                            0 if counting else sum(map(len, texts)) / 4 * 0.15 / 1e6
                        ),
                    )
                    self.write("response", r, data)
                else:
                    r.update(
                        status="FAILED",
                        error_code=response.json().get("error", {}).get("status"),
                    )
                return response
            except BaseException as error:
                r.update(status="FAILED", error_type=type(error).__name__)
                raise
            finally:
                r["elapsed_seconds"] = time.perf_counter() - started
                self.save()

        httpx.AsyncClient.post = post
