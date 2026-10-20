"""Local, explicitly budgeted authoring experiment. No production routes or writes."""

import argparse
import asyncio
import hashlib
import time
from dataclasses import replace
from pathlib import Path

from _shared.services.config_loader import get_env, load_config
from _shared.services.logger import get_logger
from _shared.services.model_gateway import ModelBackend, ModelBackendError, Request, invoke_model

from .accounting import charge, reserve
from .anthropic_trial import ClaudeReceipt, ClaudeTrialBackend, ClaudeTrialConfig
from .provider import configure_gateway, receipt_context
from .routing import TASKS, ProviderPlugin, ProviderRegistry, TaskRoute, gateway_id
from .settings import ROOT, load_settings
from .store import Database, Store

logger = get_logger(__name__)
TRIAL = ROOT / "experiments/claude-vacuum"
PRIVATE = ROOT / ".vercel/claude-vacuum/private"
GPU_TRIAL = ROOT / "experiments/gpu-study"
ART_TRIALS = (GPU_TRIAL, ROOT / "experiments/refrigerator-study")


def denied_backend(model: str) -> ModelBackend:
    """All unneeded tasks are explicitly unavailable in this isolated process."""
    raise ModelBackendError("Task is disabled in the local Claude trial")


def trial_prompt(request_path: Path) -> str:
    """Send only public kit/guidance and an inspected brief, never app data or secrets."""
    paths = [
        TRIAL / "BRIEF.md",
        ROOT / "vendor/anatomy/SKILL.md",
        ROOT / "vendor/anatomy/references/kit.md",
        ROOT / "vendor/anatomy/references/craft.md",
        ROOT / "vendor/anatomy/examples/dial-indicator/build.mjs",
        request_path,
    ]
    if request_path.name.startswith("request-art-first"):
        paths = [TRIAL / "request-art-first.md", ROOT / "vendor/anatomy/references/kit.md"]
        if request_path.name != "request-art-first.md":
            paths.append(request_path)
    if request_path.parent in ART_TRIALS and request_path.name.startswith("request-art-first"):
        paths = [request_path.parent / "BRIEF.md", request_path, ROOT / "vendor/anatomy/references/kit.md"]
    references = []
    for path in paths:
        content = path.read_text()
        if path.name == "SKILL.md":
            content = content.split("## WebGL inside the drawing")[0]
        if path.name == "craft.md":
            content = content.split("## 8. Round parts and pipes")[0]
        if path.name == "kit.md":
            content = content.split("## 12.")[0]
        references.append(f"<reference name='{path.name}'>\n{content}\n</reference>")
    return "\n\n".join(references)


async def run_trial(operation: str, request_path: Path) -> None:
    """Reserve once, checkpoint before dispatch, settle observed/uncertain billing once."""
    if not operation.replace("-", "").isalnum() or len(operation) > 60:
        raise ValueError("Use a short alphanumeric operation name")
    # JSON is a YAML subset; use the mandatory shared loader, then strict contracts.
    profile = "config-art-first.json" if request_path.name.startswith("request-art-first") else "config.json"
    config = ClaudeTrialConfig.model_validate(load_config(TRIAL / profile))
    settings = replace(load_settings(), database_url="", data_dir=PRIVATE, budget_usd=config.budget_usd)
    if settings.production:
        raise ValueError("The Claude authoring trial is local only")
    key = get_env("ANTHROPIC_API_KEY", "") or ""
    if not key:
        raise ValueError("Local Anthropic key is missing")
    prompt = trial_prompt(request_path)
    adapter = ClaudeTrialBackend(config.model, key, config)
    adapter.request_body(
        Request(
            prompt=prompt, messages=None, grammar=None, max_tokens=config.max_output_tokens, label_tokens=None
        )
    )
    config_sha = hashlib.sha256(config.model_dump_json().encode()).hexdigest()
    prompt_sha = hashlib.sha256((config_sha + prompt).encode()).hexdigest()
    result_path = PRIVATE / (operation + ".txt")
    store = Store("", PRIVATE)
    allowance = config.allowance()

    def checkpoint(db: Database) -> bool:
        old = db.jobs.get(operation)
        if old:
            if old["prompt_sha256"] != prompt_sha:
                raise ValueError("Operation identity cannot be reused for changed input")
            if old["status"] == "completed" and result_path.exists():
                digest = hashlib.sha256(result_path.read_bytes()).hexdigest()
                if old.get("output_sha256") == digest:
                    return False
            raise ValueError("Operation already dispatched; inspect its checkpoint, do not retry paid work")
        reserve(db, allowance, settings)
        db.jobs[operation] = {
            "status": "dispatched",
            "task": "authoring",
            "model": config.model,
            "prompt_sha256": prompt_sha,
            "config_sha256": config_sha,
            "config": config.model_dump(),
            "allowance_usd": allowance,
            "at": time.time(),
        }
        return True

    if not store.transaction(checkpoint):
        logger.info("Claude trial checkpoint reused", operation=operation)
        return
    PRIVATE.chmod(0o700)
    receipt = ClaudeReceipt()
    token = receipt_context.set(receipt)
    configure_gateway(
        settings,
        ProviderRegistry(
            {
                "anthropic-trial": ProviderPlugin(
                    lambda model: ClaudeTrialBackend(model, key, config), frozenset({"authoring"})
                ),
                "disabled": ProviderPlugin(denied_backend, frozenset(TASKS)),
            },
            {
                task: TaskRoute("anthropic-trial", config.model)
                if task == "authoring"
                else TaskRoute("disabled", "unavailable")
                for task in TASKS
            },
        ),
    )
    started = time.monotonic()
    try:
        result = await invoke_model(
            prompt=prompt,
            models=[gateway_id("authoring")],
            max_tokens=config.max_output_tokens,
            timeout_ms=(config.timeout_seconds + 40) * 1000,
        )
        temporary = result_path.with_suffix(".partial")
        temporary.write_text(result.text)
        temporary.chmod(0o600)
        temporary.replace(result_path)

        def settle(db: Database) -> None:
            charge(db, operation, receipt, allowance)
            db.jobs[operation].update(
                {
                    "status": "completed",
                    "output_sha256": hashlib.sha256(result.text.encode()).hexdigest(),
                    "duration_seconds": round(time.monotonic() - started, 3),
                }
            )

        store.transaction(settle)
        logger.info(
            "Claude trial completed",
            operation=operation,
            model=receipt.models,
            task="authoring",
            route=gateway_id("authoring"),
            input_tokens=receipt.input_tokens,
            output_tokens=receipt.output_tokens,
            cost_usd=receipt.cost_usd,
            duration_seconds=round(time.monotonic() - started, 3),
        )
    except Exception as exc:
        failure_type = type(exc).__name__

        def fail(db: Database) -> None:
            charge(db, operation, receipt, allowance, uncertain=not receipt.billing_complete)
            db.jobs[operation].update({"status": "failed", "failure_type": failure_type})

        store.transaction(fail)
        logger.warning(
            "Claude trial failed; no retry",
            operation=operation,
            failure_type=failure_type,
            task="authoring",
            route=gateway_id("authoring"),
            duration_seconds=round(time.monotonic() - started, 3),
        )
        raise
    finally:
        receipt_context.reset(token)
        configure_gateway(settings)


def main() -> None:
    """Run one deliberately named generation; a rerun cannot create another charge."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation", required=True)
    parser.add_argument("--request", type=Path, default=TRIAL / "request.md")
    args = parser.parse_args()
    asyncio.run(run_trial(args.operation, args.request.resolve()))


if __name__ == "__main__":
    main()
