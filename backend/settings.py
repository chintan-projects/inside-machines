"""Typed application settings resolved through the workspace config loader."""

import math
from dataclasses import dataclass
from pathlib import Path

from _shared.services.config_loader import ConfigLoader, get_env
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.local", override=False)


@dataclass(frozen=True)
class Settings:
    """Deployment configuration. Secrets never enter public API responses."""

    database_url: str
    data_dir: Path
    openai_key: str
    blob_token: str
    invite_code: str
    owner_code: str
    session_secret: str
    budget_usd: float
    model: str
    reasoning_effort: str
    provider_timeout_seconds: int
    speech_model: str
    speech_voice: str
    input_rate: float
    output_rate: float
    speech_rate: float
    generation_reserve: float
    research_phase_reserve: float
    max_research_tokens: int
    text_phase_reserve: float
    speech_phase_reserve: float
    chat_reserve: float
    max_output_tokens: int
    max_chat_tokens: int
    max_attempts: int
    lease_seconds: int
    session_days: int
    hourly_requests: int
    video_width: int
    video_height: int
    video_fps: int
    production: bool

    def __post_init__(self) -> None:
        """Reject unsafe limits rather than silently accepting an unbounded budget."""
        amounts = (
            self.budget_usd,
            self.input_rate,
            self.output_rate,
            self.speech_rate,
            self.generation_reserve,
            self.chat_reserve,
            self.text_phase_reserve,
            self.research_phase_reserve,
            self.speech_phase_reserve,
        )
        if any(not math.isfinite(n) or n < 0 for n in amounts):
            raise ValueError("Budgets and provider rates must be finite and nonnegative")
        if (
            self.generation_reserve
            < self.research_phase_reserve + 2 * self.text_phase_reserve + 7 * self.speech_phase_reserve
        ):
            raise ValueError(
                "Generation reserve must cover research, authoring, review, and up to seven narrated stages"
            )
        if (
            self.text_phase_reserve
            < (100000 * self.input_rate + self.max_output_tokens * self.output_rate) / 1e6 + 0.03
        ):
            raise ValueError("Text allowance is too small for configured model token limits and rates")
        if (
            self.research_phase_reserve
            < (100000 * self.input_rate + self.max_research_tokens * self.output_rate) / 1e6 + 0.03
            or not 1 <= self.max_research_tokens <= 4000
        ):
            raise ValueError("Research allowance/token limit cannot cover its bounded evidence request")
        if self.chat_reserve < (24000 * self.input_rate + self.max_chat_tokens * self.output_rate) / 1e6:
            raise ValueError("Chat reserve is too small for configured model token limits and rates")
        if (
            not 1 <= self.video_fps <= 24
            or not 200 <= self.video_width <= 1280
            or not 200 <= self.video_height <= 900
        ):
            raise ValueError("Video dimensions or frame rate exceed alpha bounds")
        if self.video_width % 2 or self.video_height % 2:
            raise ValueError("Video dimensions must be even for mobile-compatible encoding")
        if self.reasoning_effort not in ("low", "medium", "high"):
            raise ValueError("Unsupported reasoning effort")
        if (
            not 10 <= self.provider_timeout_seconds <= 210
            or self.lease_seconds < self.provider_timeout_seconds + 20
        ):
            raise ValueError("Provider deadline must fit inside the worker lease")
        if self.max_output_tokens < 1 or self.max_chat_tokens < 1 or self.lease_seconds < 120:
            raise ValueError(
                "Token limits must be positive and job leases must cover a bounded provider call"
            )

    @property
    def generation_enabled(self) -> bool:
        """Require both credentials and an explicitly configured spending ceiling."""
        return bool(self.openai_key and self.budget_usd > 0)


def load_settings() -> Settings:
    """Load settings without logging credentials or implicit spending authorization."""
    loader = ConfigLoader(ROOT / "config")
    loader.load("app")

    def number(key: str) -> float:
        return float(str(loader.get(key, env_var="INSIDE_" + key.upper())))

    def text(key: str) -> str:
        return str(loader.get(key, env_var="INSIDE_" + key.upper()))

    production = get_env("VERCEL") == "1"
    return Settings(
        database_url=get_env("DATABASE_URL", "") or "",
        data_dir=Path(get_env("INSIDE_DATA_DIR", "/tmp/inside" if production else ".data") or ".data"),
        openai_key=get_env("OPENAI_API_KEY", "") or "",
        blob_token=get_env("BLOB_READ_WRITE_TOKEN", "") or "",
        invite_code=get_env("INSIDE_INVITE_CODE", "") or "",
        owner_code=get_env("INSIDE_OWNER_CODE", "") or "",
        session_secret=get_env("INSIDE_SESSION_SECRET", "") or "",
        budget_usd=float(get_env("INSIDE_BUDGET_USD", "0") or "0"),
        model=text("model"),
        reasoning_effort=text("reasoning_effort"),
        provider_timeout_seconds=int(number("provider_timeout_seconds")),
        speech_model=text("speech_model"),
        speech_voice=text("speech_voice"),
        input_rate=number("input_usd_per_million"),
        output_rate=number("output_usd_per_million"),
        speech_rate=number("speech_usd_per_minute"),
        generation_reserve=number("generation_reserve_usd"),
        chat_reserve=number("chat_reserve_usd"),
        research_phase_reserve=number("research_phase_reserve_usd"),
        max_research_tokens=int(number("max_research_output_tokens")),
        text_phase_reserve=number("text_phase_reserve_usd"),
        speech_phase_reserve=number("speech_phase_reserve_usd"),
        max_output_tokens=int(number("max_output_tokens")),
        max_chat_tokens=int(number("max_chat_output_tokens")),
        max_attempts=int(number("max_job_attempts")),
        lease_seconds=int(number("lease_seconds")),
        session_days=int(number("session_days")),
        hourly_requests=int(number("max_requests_per_hour")),
        video_width=int(number("video_width")),
        video_height=int(number("video_height")),
        video_fps=int(number("video_fps")),
        production=production,
    )
