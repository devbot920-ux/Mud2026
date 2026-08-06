"""Export the fixed-width Rose spell table into an ignored, client-safe fixture.

The source database is opened immutable/read-only.  This decoder intentionally
exports only fields corroborated by RCIROSE.DLL consumers; unknown bytes remain
unknown rather than receiving invented names.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


SPHERE_NAMES = {
    1: "Forces",
    2: "Life",
    3: "Body",
    4: "Alchemy",
    5: "Correspondence",
    6: "Necromancy",
}


def u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def i16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little", signed=True)


def cstring(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("cp1252", errors="replace").strip()


def decode_spell(data: bytes) -> dict[str, object]:
    if len(data) != 405:
        raise ValueError(f"expected a 405-byte SPEL record, found {len(data)}")
    handlers = [i16(data, offset) for offset in range(389, 399, 2)]
    effects = []
    for index, handler in enumerate(handlers):
        if handler < 0:
            continue
        base = 349 + index * 8
        effects.append(
            {
                "handler": handler,
                "dice_count": data[base],
                "roll_min": data[base + 2],
                "roll_max": data[base + 4],
            }
        )
    return {
        "id": u16(data, 90),
        "name": cstring(data[0:80]),
        "abbreviation": cstring(data[80:90]),
        "sphere": data[332],
        "sphere_name": SPHERE_NAMES.get(data[332], f"Sphere {data[332]}"),
        "secondary_sphere": data[333],
        "learning_threshold": data[334],
        "proficiency_requirement": data[336],
        "secondary_requirement": data[337],
        "mana_cost": data[338],
        "effect_type": data[339],
        "base_recovery": u16(data, 340),
        "parser_kind": data[348],
        "effects": effects,
        "target_flags": list(data[399:404]),
        "damage_type": data[404],
    }


def export(source: Path, destination: Path) -> dict[str, object]:
    uri = source.resolve().as_uri() + "?mode=ro&immutable=1"
    with sqlite3.connect(uri, uri=True) as connection:
        rows = connection.execute("SELECT data FROM data_t ORDER BY key_2").fetchall()
    spells = [decode_spell(bytes(row[0])) for row in rows]
    payload = {
        "contract": {"name": "mud2026.rose-spells", "version": "1.0.0"},
        "evidence": {
            "source": source.name,
            "record_length": 405,
            "decoder": "RCIROSE.DLL casting consumers",
        },
        "spells": spells,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(r"C:\dos\modules\RCI_SPEL.db"))
    parser.add_argument("--output", type=Path, default=Path("var/exports/spells-v1.json"))
    args = parser.parse_args()
    payload = export(args.source, args.output)
    print(f"Exported {len(payload['spells'])} spells to {args.output}")


if __name__ == "__main__":
    main()
