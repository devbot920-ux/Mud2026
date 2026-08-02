#!/usr/bin/env python3
"""Create a deterministic, read-only inventory of configured source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "source_paths.local.json"
DEFAULT_OUTPUT = REPO_ROOT / "var" / "manifests" / "source-manifest.json"
CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _matches_for_source(source: dict[str, Any]) -> Iterable[Path]:
    path = Path(os.path.expandvars(source["path"])).expanduser()
    if path.is_file():
        yield path
        return
    if not path.is_dir():
        raise FileNotFoundError(f"Source path does not exist: {path}")

    patterns = source.get("include", ["*"])
    if not isinstance(patterns, list) or not patterns:
        raise ValueError(f"Source {source.get('name')!r} has no include patterns")
    for pattern in patterns:
        for candidate in path.glob(pattern):
            if candidate.is_file():
                yield candidate


def discover_sources(config: dict[str, Any]) -> list[tuple[str, Path]]:
    sources = config.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Configuration must contain a non-empty 'sources' list")

    discovered: dict[str, tuple[str, Path]] = {}
    for source in sources:
        if not isinstance(source, dict) or not source.get("name") or not source.get("path"):
            raise ValueError("Each source requires non-empty 'name' and 'path' values")
        name = str(source["name"])
        for path in _matches_for_source(source):
            resolved = path.resolve(strict=True)
            key = os.path.normcase(str(resolved))
            discovered.setdefault(key, (name, resolved))

    return sorted(discovered.values(), key=lambda item: (item[0], str(item[1]).lower()))


def build_manifest(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as source:
        config = json.load(source)

    files = []
    for source_name, path in discover_sources(config):
        stat = path.stat()
        files.append(
            {
                "source": source_name,
                "path": str(path),
                "size_bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat().replace("+00:00", "Z"),
                "sha256": sha256_file(path),
            }
        )

    latest_modified = max(
        (entry["modified_utc"] for entry in files),
        default=None,
    )
    return {
        "manifest_version": 1,
        "source_max_modified_utc": latest_modified,
        "hash_algorithm": "sha256",
        "file_count": len(files),
        "total_size_bytes": sum(entry["size_bytes"] for entry in files),
        "files": files,
    }


def write_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(manifest, output, indent=2, ensure_ascii=False)
        output.write("\n")
    temporary.replace(output_path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify inputs and print a summary without writing a manifest",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_manifest(args.config.resolve(strict=True))
        if not args.check:
            write_manifest(manifest, args.output.resolve())
        action = "Verified" if args.check else "Inventoried"
        print(
            f"{action} {manifest['file_count']} files "
            f"({manifest['total_size_bytes']} bytes)."
        )
        if not args.check:
            print(f"Manifest: {args.output.resolve()}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
