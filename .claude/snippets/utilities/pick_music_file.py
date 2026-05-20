# From: app.py:252
# Open a native file picker; copy the chosen audio into AppData as

    def pick_music_file(self) -> dict:
        """Open a native file picker; copy the chosen audio into AppData as
        user_bg_music<ext>. Returns {ok, name, ext} or {ok:False,...}.
        """
        import shutil
        try:
            import webview  # local import keeps module import-safe in dev
            windows = getattr(webview, "windows", None) or []
            if not windows:
                return {"ok": False, "error": "no window"}
            win = windows[0]
            file_types = ("Audio files (*.ogg;*.mp3;*.wav;*.m4a)", "All files (*.*)")
            result = win.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        except Exception as exc:  # pywebview dialog can raise on some backends
            log.warning("pick_music_file dialog failed: %s", exc)
            _log_event("boundary", "pick_music_file", {"ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        if not result:
            return {"ok": False, "error": "cancelled"}
        chosen = Path(result[0] if isinstance(result, (list, tuple)) else result)
        ext = chosen.suffix.lower() or ".ogg"
        if ext not in (".ogg", ".mp3", ".wav", ".m4a"):
            return {"ok": False, "error": "unsupported file type"}
        # Cap at 12 MB — a between-lessons loop should be tiny; refuse a full album.
        try:
            if chosen.stat().st_size > 12 * 1024 * 1024:
                return {"ok": False, "error": "file too big (max 12 MB)"}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        # Clear any prior user track (different ext) so only one exists.
        for old in _appdata_root().glob("user_bg_music.*"):
            try:
                old.unlink()
            except OSError as exc:
                # Locked file (being read?) would leave two tracks; glob order
                # could then play the wrong one. Surface it loudly.
                log.warning("pick_music_file: could not remove old track %s: %s", old, exc)
        dest = _appdata_root() / f"user_bg_music{ext}"
        try:
            shutil.copy2(chosen, dest)
        except OSError as exc:
            log.warning("pick_music_file copy failed: %s", exc)
            _log_event("boundary", "pick_music_file", {"ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        _log_event("boundary", "pick_music_file", {"ok": True, "name": chosen.name, "ext": ext})
        return {"ok": True, "name": chosen.name, "ext": ext}
