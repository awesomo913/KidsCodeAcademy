# From: app.py:327
# v0.7.11 Fix 10: enumerate saved capstone JSON projects.

    def list_kid_projects(self) -> list[dict]:
        """v0.7.11 Fix 10: enumerate saved capstone JSON projects.

        Walks kid_projects/ looking for *.json files saved by the share-card
        handler in lesson 60. Returns one entry per project with name, filename,
        and ISO created date. Used by Parent Corner 'Projects' tab.

        Best-effort: any unreadable / non-JSON file is skipped silently
        (kid scribbles or older TXT shares would otherwise crash the list).
        """
        import json
        user_dir = get_user_data_dir()
        items: list[dict] = []
        try:
            for fp in sorted(user_dir.glob("*.json")):
                try:
                    raw = fp.read_text(encoding="utf-8")
                    obj = json.loads(raw)
                except (OSError, json.JSONDecodeError):
                    continue
                # Friendly name: capstone uses game_name; level saves get a
                # readable "My Level" + date instead of the raw kid_level_<ts>.
                stem = fp.stem
                if obj.get("game_name"):
                    nice = str(obj["game_name"])
                elif stem.startswith("kid_level_"):
                    nice = "My Level"
                else:
                    nice = stem
                items.append({
                    "filename": fp.name,
                    "name": nice,
                    "created": str(obj.get("created_at") or obj.get("savedAt") or ""),
                    "kind": str(obj.get("kind") or ("level" if "grid" in obj else "project")),
                })
        except OSError as exc:
            log.warning("list_kid_projects failed: %s", exc)
            _log_event("boundary", "list_kid_projects", {"target": str(user_dir), "ok": False, "err": str(exc)})
            return []
        _log_event("boundary", "list_kid_projects", {"target": str(user_dir), "ok": True, "count": len(items)})
        return items
