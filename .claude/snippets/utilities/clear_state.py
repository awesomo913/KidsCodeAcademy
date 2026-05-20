# From: app.py:235
# Delete state.json. Called only on explicit Reset all progress.

    def clear_state(self) -> dict:
        """Delete state.json. Called only on explicit Reset all progress."""
        target = get_state_file()
        try:
            if target.is_file():
                target.unlink()
        except OSError as exc:
            log.warning("clear_state failed: %s", exc)
            return {"ok": False, "error": str(exc)}
        return {"ok": True}
