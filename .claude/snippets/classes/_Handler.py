# From: app.py:444

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a: object, **kw: object) -> None:
            super().__init__(*a, directory=serve_dir_str, **kw)

        def log_message(self, fmt: str, *args: object) -> None:
            # Silence the per-request stderr spam — pywebview's window already
            # logs the page URL on load.
            pass
