# From: app.py:487
# Background-thread function passed to webview.start().

def _schedule_headless_close(window: "webview.Window", secs: int) -> None:
    """Background-thread function passed to webview.start().

    pywebview calls this after the GUI loop is up. We arm a Timer that asks the
    window to destroy itself N seconds later. window.destroy() is thread-safe
    in pywebview — it marshals to the GUI thread internally.
    """
    log.info("headless mode: scheduling auto-close in %ds", secs)
    _log_event("state", "headless.armed", {"secs": secs})

    def _close() -> None:
        log.info("headless: timer fired — closing window after %ds", secs)
        _log_event("state", "headless.firing", {"secs": secs})
        try:
            window.destroy()
        except Exception as exc:  # pragma: no cover — best-effort cleanup
            log.warning("window.destroy() failed: %s", exc)
            _log_event("failure", "headless.destroy", {"err": str(exc)})

    threading.Timer(secs, _close).start()
