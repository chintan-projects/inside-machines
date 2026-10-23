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
    authoring_provider: str = "openai"
    anthropic_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"
    anthropic_input_rate: float = 2.0
    anthropic_output_rate: float = 10.0
    anthropic_cache_write_rate: float = 4.0
    anthropic_cache_read_rate: float = 0.10
    anthropic_max_input_bytes: int = 100000
    public_access: bool = False

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
        if self.authoring_provider not in ("openai", "anthropic"):
            raise ValueError("Unsupported trusted authoring provider")
        if self.authoring_provider == "anthropic":
            rates = (
                self.anthropic_input_rate,
                self.anthropic_output_rate,
                self.anthropic_cache_write_rate,
                self.anthropic_cache_read_rate,
            )
            if self.anthropic_model != "claude-sonnet-5-5":
                raise ValueError("Claude authoring model requires a verified pricing/contract revision")
            if any(not math.isfinite(rate) or rate < minimum for rate, minimum in zip(rates, (2, 10, 4, .1), strict=True)):
                raise ValueError("Claude authoring rates must cover the verified model prices")
            if not 1024 <= self.anthropic_max_input_bytes <= 100000 or self.max_output_tokens > 32000:
                raise ValueError("Claude authoring token/context bounds exceed the tested route")
            ceiling = (
                (self.anthropic_max_input_bytes + 4096) * max(rates[0], rates[2], rates[3])
                + self.max_output_tokens * rates[1]
            ) / 1e6 + 0.03
            if self.text_phase_reserve < ceiling:
                raise ValueError("Text allowance cannot cover the configured Claude authoring route")

    @property
    def generation_enabled(self) -> bool:
        """Require both credentials and an explicitly configured spending ceiling."""
        return bool(
            self.openai_key
            and self.budget_usd > 0
            and (self.authoring_provider != "anthropic" or self.anthropic_key)
        )


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
        authoring_provider=text("authoring_provider"),
        anthropic_key=get_env("ANTHROPIC_API_KEY", "") or "",
        anthropic_model=text("anthropic_model"),
        anthropic_input_rate=number("anthropic_input_usd_per_million"),
        anthropic_output_rate=number("anthropic_output_usd_per_million"),
        anthropic_cache_write_rate=number("anthropic_cache_write_usd_per_million"),
        anthropic_cache_read_rate=number("anthropic_cache_read_usd_per_million"),
        anthropic_max_input_bytes=int(number("anthropic_max_input_bytes")),
        public_access=get_env("INSIDE_PUBLIC_ACCESS", "false") == "true",
    )
