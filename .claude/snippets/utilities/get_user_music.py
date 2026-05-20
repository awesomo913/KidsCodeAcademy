# From: app.py:299
# Return the parent's saved track as a base64 data URL, or '' if none.

    def get_user_music(self) -> str:
        """Return the parent's saved track as a base64 data URL, or '' if none.
        Read on demand by the Ambient player so the bytes never touch
        localStorage / state.json.
        """
        import base64
        for fp in _appdata_root().glob("user_bg_music.*"):
            try:
                # Guard the read path too (not just pick): a 12 MB file becomes
                # ~16 MB base64 over the pywebview bridge. Refuse oversize so the
                # bridge doesn't silently drop/truncate an enormous response.
                if fp.stat().st_size > 12 * 1024 * 1024:
                    log.warning("get_user_music: %s too big (%d bytes), skipping", fp, fp.stat().st_size)
                    return ""
                data = fp.read_bytes()
            except OSError as exc:
                log.warning("get_user_music read failed: %s", exc)
                return ""
            ext = fp.suffix.lower().lstrip(".")
            mime = {"ogg": "audio/ogg", "mp3": "audio/mpeg",
                    "wav": "audio/wav", "m4a": "audio/mp4"}.get(ext, "audio/ogg")
            b64 = base64.b64encode(data).decode("ascii")
            return f"data:{mime};base64,{b64}"
        return ""
