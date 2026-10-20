"""Owner revision admission uses the existing budget/deduplication domain path."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException

from backend.contracts import LessonSpec
from backend.domain import Domain, User
from backend.settings import Settings
from backend.store import Store


def test_owner_revision_is_atomic_idempotent_and_preserves_parent(
    seeded: Store, settings: Settings, user: User, spec: LessonSpec
) -> None:
    """Concurrent clicks reserve one job and never modify existing lesson bytes."""
    owner = User(id="synthetic-owner", name="Synthetic test owner", owner=True)
    domain = Domain(seeded, settings)
    with pytest.raises(HTTPException):
        domain.request(spec.question, user, revision_of=spec.canonical, operation="test-operation")
    before = seeded.snapshot()

    def request(_: int) -> dict[str, object]:
        return domain.request(spec.question, owner, revision_of=spec.canonical, operation="test-operation")

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(request, range(12)))
    after = seeded.snapshot()
    assert len({str(r["job_id"]) for r in results}) == 1 and len(after.jobs) == 1
    assert after.reserved == settings.generation_reserve and after.lessons == before.lessons
    job_id = str(results[0]["job_id"])
    seeded.transaction(lambda db: db.jobs[job_id].update(status="failed"))
    with pytest.raises(HTTPException, match="409"):
        request(0)
    result = domain.request(
        spec.question, owner, revision_of=spec.canonical, operation="explicit-new-operation"
    )
    assert result["kind"] == "job" and result["job_id"] != job_id
