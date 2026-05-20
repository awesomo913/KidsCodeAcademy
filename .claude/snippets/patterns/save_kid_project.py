# From: app.py:181

    def save_kid_project(self, filename: str, data: str) -> dict:
        safe_name = "".join(c for c in filename if c.isalnum() or c in ("_", "-", "."))
        if not safe_name:
            return {"ok": False, "error": "invalid filename"}
        target = get_user_data_dir() / safe_name
        try:
            target.write_text(data, encoding="utf-8")
        except OSError as exc:
            log.warning("save_kid_project failed: %s", exc)
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "path": str(target)}
