"""Opaque family sessions with server-side revocation and throttled invite entry."""

import hashlib
import hmac
import secrets
import time

from fastapi import HTTPException

from .domain import Domain, User
from .rate_limits import take_rate
from .settings import Settings
from .store import Database, Store

COOKIE = "inside_session"


class Auth:
    """Keep bearer credentials out of persistent records and API projections."""

    def __init__(self, store: Store, settings: Settings) -> None:
        """Use the same durable repository as the catalog."""
        self.store, self.settings = store, settings

    def digest(self, value: str) -> str:
        """Hash tokens and client addresses with the deployment secret."""
        return hmac.new(self.settings.session_secret.encode(), value.encode(), hashlib.sha256).hexdigest()

    def login(self, name: str, code: str, address: str) -> tuple[User, str]:
        """Validate a family or owner invite and issue a fresh opaque session."""
        if not self.settings.session_secret or not (self.settings.invite_code or self.settings.public_access and self.settings.owner_code):
            raise HTTPException(503, "Family access hasn't been configured by the owner yet.")
        address_hash = self.digest(address)

        def attempt(db: Database) -> tuple[User, str] | None:
            message = "Too many invite attempts. Please try again in 15 minutes."
            take_rate(db, "login", address_hash, 10, message, seconds=900, consume=False)
            owner = bool(self.settings.owner_code and secrets.compare_digest(code, self.settings.owner_code))
            if not owner and not (self.settings.invite_code and secrets.compare_digest(code, self.settings.invite_code)):
                take_rate(db, "login", address_hash, 10, message, seconds=900)
                db.events.append({"kind": "login_failed", "address": address_hash, "at": time.time()})
                return None
            token = secrets.token_urlsafe(40)
            user = User(id=secrets.token_urlsafe(18), name=name.strip(), owner=owner)
            db.users[user.id] = user.model_dump()
            db.sessions[self.digest(token)] = {
                "user_id": user.id,
                "expires": time.time() + self.settings.session_days * 86400,
            }
            Domain.event(db, "login", user)
            return user, token

        result = self.store.transaction(attempt)
        if result is None:
            raise HTTPException(401, "That invite code isn't valid.")
        return result

    def user(self, token: str | None) -> User:
        """Require a live session, with identical errors for all invalid credentials."""
        if not token:
            raise HTTPException(401, "Enter your family invite to continue.")

        def read(db: Database) -> User:
            session = db.sessions.get(self.digest(token))
            if not session or float(str(session["expires"])) <= time.time():
                raise HTTPException(401, "Your session has expired. Please sign in again.")
            user = db.users.get(str(session["user_id"]))
            if not user:
                raise HTTPException(401, "Please sign in again.")
            return User.model_validate(user)

        return self.store.transaction(read, write=False)

    def reader(self, token: str | None) -> User:
        """Public reads never mint a shared session or identify unrelated visitors together."""
        if token or not self.settings.public_access:
            try:
                return self.user(token)
            except HTTPException as exc:
                if not self.settings.public_access or exc.status_code != 401:
                    raise
        return User(id="", name="Visitor", owner=False, guest=True)

    def guest(self, token: str | None, address: str) -> tuple[User, str | None]:
        """Reuse a valid browser session or issue a unique, rate-limited anonymous one."""
        if not self.settings.public_access:
            raise HTTPException(404, "Public access is not enabled")
        if not self.settings.session_secret:
            raise HTTPException(503, "Public browser sessions are not configured")
        if token:
            try:
                return self.user(token), None
            except HTTPException as exc:
                if exc.status_code != 401:
                    raise
        address_hash = self.digest(address)

        def issue(db: Database) -> tuple[User, str]:
            take_rate(db, "guest", address_hash, 20, "Too many new browser sessions. Please try again later.")
            fresh = secrets.token_urlsafe(40)
            user = User(id=secrets.token_urlsafe(18), name="Visitor", owner=False, guest=True)
            db.users[user.id] = {**user.model_dump(), "address_hash": address_hash}
            db.sessions[self.digest(fresh)] = {"user_id": user.id, "expires": time.time() + self.settings.session_days * 86400}
            Domain.event(db, "guest_started", user, address=address_hash)
            return user, fresh

        return self.store.transaction(issue)

    def logout(self, token: str | None) -> None:
        """Revoke this browser's session without affecting other family members."""

        def revoke(db: Database) -> None:
            if token:
                db.sessions.pop(self.digest(token), None)

        self.store.transaction(revoke)
