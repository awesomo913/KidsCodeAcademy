# From: app.py:427
# Spin up a tiny loopback HTTP server pointed at serve_dir; return the

def _start_local_http_server(serve_dir: Path) -> int:
    """Spin up a tiny loopback HTTP server pointed at serve_dir; return the
    randomly-assigned port.

    Why: on Linux/Pi, WebKitGTK 2.40+ sandboxes file:// URLs and silently
    blocks fetch() of sibling resources (lessons/*.json, assets/*.wav).
    Loading the bundle over http://127.0.0.1:<port>/ sidesteps that —
    everything runs from a real origin. Same code path works on Windows too;
    no functional difference, and it future-proofs against any
    WebView2 file-URL tightening down the road.
    """
    import http.server
    import socketserver
    import threading

    serve_dir_str = str(serve_dir)

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a: object, **kw: object) -> None:
            super().__init__(*a, directory=serve_dir_str, **kw)

        def log_message(self, fmt: str, *args: object) -> None:
            # Silence the per-request stderr spam — pywebview's window already
            # logs the page URL on load.
            pass

    # Subclass so we can flip allow_reuse_address — without this, a rapid
    # close-then-reopen of the exe can hit "address in use" if the OS picks
    # the same random port both times before TIME_WAIT clears.
    class _ReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = _ReuseTCPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(
        target=server.serve_forever,
        name="kca-http",
        daemon=True,
    )
    thread.start()
    return port
