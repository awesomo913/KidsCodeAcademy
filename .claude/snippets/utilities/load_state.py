# From: app.py:216
# Return state.json contents as a string (empty if no file).

    def load_state(self) -> str:
        """Return state.json contents as a string (empty if no file)."""
        target = get_state_file()
        if not target.is_file():
            log.info("load_state: no file at %s (fresh install)", target)
            _log_event("boundary", "load_state", {"target": str(target), "ok": True, "exists": False})
            return ""
        t0 = time.monotonic()
        try:
            data = target.read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("load_state failed: %s", exc)
            _log_event("boundary", "load_state", {"target": str(target), "ok": False, "err": str(exc)})
            return ""
        ms = (time.monotonic() - t0) * 1000.0
        log.info("load_state ok bytes=%d path=%s (%.1fms)", len(data), target, ms)
        _log_event("boundary", "load_state", {"target": str(target), "ok": True, "ms": round(ms, 1), "bytes": len(data)})
        return data
