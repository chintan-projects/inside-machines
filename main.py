"""Vercel and local ASGI entry point."""

from backend.app import create_app

app = create_app()
# A literal build directory lets Vercel promote the generated shell, including
# its versioned service worker, rather than only the raw public/ inputs.
app.frontend("/", directory="dist", check_dir=False)
