#!/usr/bin/env python3
"""Serve the repository-local fixture viewer and ignored export."""
from __future__ import annotations

import argparse, functools, http.server, webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_server(host: str, port: int) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    return http.server.ThreadingHTTPServer((host, port), handler)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    server = make_server(args.host, args.port)
    url = f"http://{args.host}:{server.server_port}/viewer/"
    print(f"Fixture viewer: {url}")
    if not args.no_open: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0


if __name__ == "__main__": raise SystemExit(main())
