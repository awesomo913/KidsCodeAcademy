# From: app.py:74
# Writable per-user folder for kid project saves (Lesson 16).

def get_user_data_dir() -> Path:
    """Writable per-user folder for kid project saves (Lesson 16)."""
    user_dir = _appdata_root() / "kid_projects"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir
