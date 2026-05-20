# From: app.py:193
# Atomically write state.json. JS calls this on every progress update.

    def save_state(self, json_blob: str) -> dict:
        """Atomically write state.json. JS calls this on every progress update."""
        if not isinstance(json_blob, str):
            return {"ok": False, "error": "json_blob must be a string"}
        # Cap at 4 MB defensively — kid state should never approach this
        if len(json_blob) > 4 * 1024 * 1024:
            return {"ok": False, "error": "state too large"}
        target = get_state_file()
        tmp = target.with_suffix(".json.tmp")
        t0 = time.monotonic()
        try:
            tmp.write_text(json_blob, encoding="utf-8")
            os.replace(tmp, target)  # atomic on Windows + POSIX
        except OSError as exc:
            log.warning("save_state failed: %s", exc)
            _log_event("boundary", "save_state", {"target": str(target), "ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        ms = (time.monotonic() - t0) * 1000.0
        # Visible on stdout/stderr so headless workflow artifacts capture the proof.
        log.info("save_state ok bytes=%d path=%s (%.1fms)", len(json_blob), target, ms)
        _log_event("boundary", "save_state", {"target": str(target), "ok": True, "ms": round(ms, 1), "bytes": len(json_blob)})
        return {"ok": True, "path": str(target)}
