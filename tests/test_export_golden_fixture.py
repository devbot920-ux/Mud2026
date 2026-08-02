import base64
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import export_golden_fixture as exporter


class GoldenFixtureExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "baseline.sqlite"
        self.graph = self.root / "graph.json"
        connection = sqlite3.connect(self.database)
        connection.executescript((exporter.ROOT / "schema" / "baseline.sql").read_text(encoding="utf-8"))
        connection.execute("INSERT INTO source_file VALUES(1,'RCI_MOD1','RCI_MOD1.db',1,?)", ("a" * 64,))

        def raw(source_row_id, owner, tag):
            data = bytearray(223); data[:4] = int(owner).to_bytes(4, "little"); data[8] = tag
            identity = json.dumps({"id": source_row_id, "key_0": owner, "source_ordinal": source_row_id}, separators=(",", ":"))
            connection.execute("INSERT INTO source_row VALUES(?,1,'data_t',?,?,?)",
                               (source_row_id, source_row_id, identity, hashlib.sha256(data).hexdigest()))
            for ordinal, (name, kind, integer, blob) in enumerate((("key_0", "integer", owner, None), ("data", "blob", None, bytes(data)))):
                payload = blob if blob is not None else str(integer).encode()
                connection.execute("""INSERT INTO source_value(source_row_id,column_ordinal,column_name,storage_class,integer_value,blob_value,byte_length,value_sha256)
                  VALUES(?,?,?,?,?,?,?,?)""", (source_row_id, ordinal, name, kind, integer, blob, len(blob) if blob else None, hashlib.sha256(payload).hexdigest()))

        records = [(1,1,0x0A),(2,2,0x0A),(3,3,0x0A),(4,1,0x30),(5,9,0x28),(6,8,0x32),(7,1,0x0D),(8,1,0xFE)]
        for record in records: raw(*record)

        def entity(entity_type, stable_id, source_row_id):
            cursor = connection.execute("INSERT INTO decoded_entity(entity_type,stable_id,source_row_id) VALUES(?,?,?)",
                                        (entity_type, f"{entity_type}:{stable_id}", source_row_id))
            return cursor.lastrowid

        room1, room2, room3 = entity("room",1,1), entity("room",2,2), entity("room",3,3)
        spawn = entity("spawn",1,4); entity("npc",9,5); entity("item",8,6); entity("door",1,7)

        def field(eid, rid, name, value, offset=0):
            connection.execute("""INSERT INTO decoded_field(decoded_entity_id,source_row_id,field_name,value_json,byte_offset,byte_width,decoding_rule,confidence)
              VALUES(?,?,?,?,?,1,'test rule','tentative')""", (eid,rid,name,json.dumps(value),offset))

        for eid, rid, room_id in ((room1,1,1),(room2,2,2),(room3,3,3)): field(eid,rid,"room_id",room_id)
        field(spawn,4,"spawn_id",1); field(spawn,4,"spawn_count",2,221)
        field(spawn,4,"spawn_1_id",9,10); field(spawn,4,"spawn_1_count",1,70); field(spawn,4,"spawn_1_type","npc",10)
        field(spawn,4,"spawn_2_id",8,12); field(spawn,4,"spawn_2_count",2,71); field(spawn,4,"spawn_2_type","item",12)
        connection.execute("""INSERT INTO topology_edge(topology_edge_id,from_room,direction,to_room,door,hidden,direction_offset,target_offset,source_row_id)
          VALUES(1,1,'E',2,0,0,170,30,1)""")
        connection.execute("""INSERT INTO topology_edge(topology_edge_id,from_room,direction,to_room,door,hidden,direction_offset,target_offset,source_row_id)
          VALUES(2,1,'NE',2,1,0,171,34,7)""")
        connection.execute("""INSERT INTO topology_edge(topology_edge_id,from_room,direction,to_room,door,hidden,direction_offset,target_offset,source_row_id)
          VALUES(3,2,'D',3,0,0,170,30,2)""")
        connection.execute("INSERT INTO import_run VALUES(1,1,?,1,8,16)", ("b" * 64,))
        connection.commit(); connection.close()
        self.graph.write_text(json.dumps({"nodes":[
            {"id":"1","r":"R02","x":0,"y":0},{"id":"2","r":"R02","x":1,"y":0},{"id":"3","r":"R99","x":1,"y":-1}],
            "edges":[],"regionNames":{"R02":"Pendelhaven","R99":"Outside"}}), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_boundary_multiedges_entities_and_references(self):
        document = exporter.build_export(self.database, self.graph)
        self.assertEqual(document["fixture"]["primary_room_ids"], [1,2])
        self.assertEqual(document["fixture"]["stub_room_ids"], [3])
        self.assertEqual([field["name"] for field in next(room for room in document["rooms"] if room["id"] == 3)["fields"]], ["room_id"])
        self.assertEqual(len(document["edges"]), 3)
        self.assertEqual([(e["from_room"],e["to_room"]) for e in document["edges"]].count((1,2)), 2)
        self.assertEqual({entity["id"] for entity in document["npcs"]}, {9})
        self.assertEqual({entity["id"] for entity in document["items"]}, {8})
        self.assertEqual(document["spawns"][0]["entries"][0]["entity_type"], "npc")
        self.assertEqual(len(document["doors"]), 1)
        exporter.validate_export(document)

    def test_unknown_modifier_preserves_complete_raw_record(self):
        document = exporter.build_export(self.database, self.graph)
        unknown = next(item for item in document["modifiers"] if item["tag"] == "0xFE")
        self.assertIsNone(unknown["name"]); self.assertEqual(unknown["confidence"], "unknown")
        self.assertEqual(len(base64.b64decode(unknown["raw_data_base64"])), 223)

    def test_output_is_deterministic_and_atomic(self):
        first = exporter.build_export(self.database, self.graph)
        second = exporter.build_export(self.database, self.graph)
        self.assertEqual(first, second)
        output = self.root / "nested" / "fixture.json"
        exporter.write_atomic(output, first); initial = output.read_bytes()
        exporter.write_atomic(output, second); self.assertEqual(output.read_bytes(), initial)

    def test_referential_integrity_rejects_dangling_edge(self):
        document = exporter.build_export(self.database, self.graph)
        document["edges"][0]["to_room"] = 999
        with self.assertRaisesRegex(ValueError, "Dangling edge"):
            exporter.validate_export(document)

    def test_tracked_schema_identifies_exact_contract(self):
        schema = json.loads((exporter.ROOT / "schema" / "engine-neutral-export-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["contract"]["properties"]["name"]["const"], exporter.CONTRACT_NAME)
        self.assertEqual(schema["properties"]["contract"]["properties"]["version"]["const"], exporter.CONTRACT_VERSION)

    def test_viewer_loads_only_the_ignored_export(self):
        viewer = (exporter.ROOT / "viewer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("/var/exports/pendelhaven-v1.json", viewer)
        self.assertNotIn("raw_data_base64", viewer)


if __name__ == "__main__": unittest.main()
