import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import baseline_import as bi


def make_source(path: Path, rows, with_extra=False):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE data_t(id INTEGER PRIMARY KEY, data BLOB NOT NULL, key_0 INTEGER, key_1 INTEGER)")
    con.execute("CREATE INDEX key_0_index ON data_t(key_0)")
    con.execute("CREATE TABLE metadata_t(label TEXT, payload BLOB)")
    con.execute("INSERT INTO metadata_t VALUES(?,?)", ("méta", b"\x00\xff"))
    if with_extra:
        con.execute("CREATE VIEW data_ids AS SELECT id FROM data_t")
        con.execute("CREATE TRIGGER keep_rows BEFORE DELETE ON data_t BEGIN SELECT RAISE(ABORT, 'immutable'); END")
    con.executemany("INSERT INTO data_t VALUES(?,?,?,?)", rows)
    con.commit(); con.close()


def mod_blob(obj_id, tag, short=b"sample", links=()):
    blob = bytearray(224); blob[:4] = obj_id.to_bytes(4, "little"); blob[8] = tag
    blob[70:70 + len(short)] = short
    for slot, (ordinal, target) in enumerate(links):
        blob[170 + slot] = ordinal; blob[30 + slot * 4:34 + slot * 4] = target.to_bytes(4, "little")
    return bytes(blob)


def modifier_blob(obj_id, tag, size=224, values=()):
    blob=bytearray(size)
    if size>=4: blob[:4]=obj_id.to_bytes(4,"little")
    if size>8: blob[8]=tag
    for offset,value in values:
        if isinstance(value,bytes): blob[offset:offset+len(value)]=value
        else: blob[offset]=value
    return bytes(blob)


class BaselineImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)

    def tearDown(self): self.tmp.cleanup()

    def sources(self):
        mod = self.root / "RCI_MOD1.db"; des = self.root / "RCI_DES1.db"
        unknown = mod_blob(99, 0xFE)
        rows = [(1, mod_blob(1, 0x0A, links=((1, 2),)), 1, 10),
                (2, mod_blob(2, 0x0A), 2, 20), (3, unknown, 99, 30), (4, b"tiny", 100, 40),
                (5, modifier_blob(1,0x85,values=((70,2),(71,10),(72,1))), 1, 50),
                (6, modifier_blob(1,0x48,values=((70,250),(71,20),(72,2))), 1, 60),
                (7, modifier_blob(1,0x75,values=((10,9),)), 1, 70),
                (8, modifier_blob(1,0x6E,values=((220,4),)), 1, 80),
                (9, modifier_blob(1,0xC5,values=((70,b"Find\0the rose\0"),)), 1, 90),
                (10, mod_blob(50,0x32), 50, 100), (11, modifier_blob(50,0x33), 50, 110),
                (12, modifier_blob(2,0x48,size=9), 2, 120),
                (13, modifier_blob(2,0x85,size=71,values=((70,255),)), 2, 130)]
        make_source(mod, rows, with_extra=True)
        make_source(des, [(1, (1).to_bytes(4,"little") + b"\0Long text\0ignored", 1, 1)])
        return [des, mod]

    def test_preserves_every_row_value_blob_hash_and_schema_object(self):
        paths=self.sources(); before={p:bi.sha256_file(p) for p in paths}; out=self.root/"out.sqlite"
        result=bi.import_all(paths,out)
        self.assertEqual(before,{p:bi.sha256_file(p) for p in paths})
        con=sqlite3.connect(out)
        raw=con.execute("SELECT blob_value,value_sha256 FROM source_value WHERE column_name='data' AND byte_length=224 ORDER BY source_value_id LIMIT 1").fetchone()
        expected=mod_blob(1,0x0A,links=((1,2),)); self.assertEqual(raw[0],expected)
        self.assertEqual(raw[1],hashlib.sha256(expected).hexdigest())
        self.assertEqual(con.execute("SELECT byte_length FROM source_value WHERE text_value='méta'").fetchone()[0],len("méta".encode("utf-8")))
        types={r[0] for r in con.execute("SELECT object_type FROM schema_object WHERE object_name IN ('data_ids','keep_rows')")}
        self.assertEqual(types,{"view","trigger"}); self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
        self.assertEqual(result["source_count"],2)
        con.close()

    def test_unknown_and_truncated_mod1_tags_are_cataloged(self):
        paths=self.sources(); out=self.root/"out.sqlite"; result=bi.import_all(paths,out)
        con=sqlite3.connect(out)
        self.assertEqual(con.execute("SELECT record_count FROM mod1_tag_catalog WHERE tag=254").fetchone()[0],1)
        self.assertEqual(con.execute("SELECT record_count FROM mod1_tag_catalog WHERE tag IS NULL").fetchone()[0],1)
        self.assertEqual(result["truncated_mod1_records"],1)
        con.close()

    def test_known_decode_has_offsets_confidence_and_topology(self):
        paths=self.sources(); out=self.root/"out.sqlite"; bi.import_all(paths,out); con=sqlite3.connect(out)
        field=con.execute("SELECT byte_offset,byte_width,confidence FROM decoded_field WHERE field_name='room_id' ORDER BY decoded_field_id LIMIT 1").fetchone()
        self.assertEqual(field,(0,4,"strong"))
        self.assertEqual(con.execute("SELECT from_room,direction,to_room,door,direction_offset,target_offset FROM topology_edge").fetchone(),(1,"N",2,0,170,30))
        text=con.execute("SELECT value_json FROM decoded_field WHERE field_name='text'").fetchone()[0]
        self.assertIn("Long text",text); self.assertNotIn("ignored",text)
        con.close()

    def test_room_modifiers_have_offsets_unknown_codes_and_modifier_provenance(self):
        paths=self.sources(); out=self.root/"out.sqlite"; bi.import_all(paths,out); con=sqlite3.connect(out)
        rows=con.execute("""SELECT f.field_name,f.value_json,f.byte_offset,f.byte_width,f.confidence,r.source_identity_json
          FROM decoded_field f JOIN decoded_entity e USING(decoded_entity_id) JOIN source_row r ON r.source_row_id=f.source_row_id
          WHERE e.stable_id='room:1' AND f.field_name IN
          ('attribute_code','attribute_name','attribute_max','attribute_min','skill_code','skill_name','skill_max','skill_min','promotion_max','spells_count','quest_text')""").fetchall()
        fields={r[0]:r for r in rows}
        self.assertEqual((fields['attribute_code'][1],fields['attribute_code'][2:5]),('2',(70,1,'tentative')))
        self.assertEqual(fields['attribute_name'][1],'"dexterity"')
        self.assertEqual(fields['skill_code'][1],'250'); self.assertEqual(fields['skill_name'][1],'null')
        self.assertEqual(fields['promotion_max'][2:4],(10,1)); self.assertEqual(fields['spells_count'][2:4],(220,1))
        self.assertEqual(fields['quest_text'][1],'"Find ... the rose"')
        self.assertIn('"id":5',fields['attribute_code'][5]); self.assertIn('"id":6',fields['skill_code'][5])
        self.assertIn('"id":7',fields['promotion_max'][5]); self.assertIn('"id":8',fields['spells_count'][5]); self.assertIn('"id":9',fields['quest_text'][5])
        truncated=con.execute("""SELECT count(*) FROM decoded_field f JOIN decoded_entity e USING(decoded_entity_id)
          WHERE e.stable_id='room:2' AND f.field_name LIKE 'skill_%'""").fetchone()[0]
        self.assertEqual(truncated,0)
        partial=dict(con.execute("""SELECT f.field_name,f.value_json FROM decoded_field f JOIN decoded_entity e USING(decoded_entity_id)
          WHERE e.stable_id='room:2' AND f.field_name LIKE 'attribute_%'""").fetchall())
        self.assertEqual(partial,{'attribute_code':'255','attribute_name':'null'})
        category=con.execute("""SELECT f.byte_offset,f.confidence,r.source_identity_json FROM decoded_field f
          JOIN decoded_entity e USING(decoded_entity_id) JOIN source_row r ON r.source_row_id=f.source_row_id
          WHERE e.stable_id='item:50' AND f.field_name='category_weapon'""").fetchone()
        self.assertEqual(category[:2],(8,'tentative')); self.assertIn('"id":11',category[2])
        con.close()

    def test_output_is_byte_deterministic_and_idempotent(self):
        paths=self.sources(); out=self.root/"out.sqlite"
        one=bi.import_all(paths,out); first=out.read_bytes(); two=bi.import_all(paths,out)
        self.assertEqual(first,out.read_bytes()); self.assertEqual(one,two)

    def test_failure_does_not_replace_existing_output(self):
        bad=self.root/"bad.db"; bad.write_bytes(b"not sqlite"); out=self.root/"out.sqlite"; out.write_bytes(b"keep")
        with self.assertRaises(sqlite3.DatabaseError): bi.import_all([bad],out)
        self.assertEqual(out.read_bytes(),b"keep")

    def test_parse_links_handles_truncation_and_unknown_ordinals(self):
        self.assertEqual(bi.parse_links(b"short"),[])
        blob=bytearray(224); blob[170]=255; blob[171]=2; blob[30:34]=(7).to_bytes(4,"little")
        self.assertEqual(bi.parse_links(bytes(blob)),[("S",7,171,30)])

    def test_reconciliation_reports_published_and_additional_edges(self):
        paths=self.sources(); out=self.root/"out.sqlite"; bi.import_all(paths,out)
        graph_path=self.root/"graph.json"
        graph_path.write_text(json.dumps({
            "nodes":[{"id":"1"},{"id":"2"}],
            "edges":[],
        }),encoding="utf-8")
        result=bi.reconcile(out,graph_path)
        self.assertEqual(result["generated_nodes"],2)
        self.assertEqual(result["graph_nodes"],2)
        self.assertEqual(result["missing_nodes_count"],0)
        self.assertEqual(result["extra_nodes_count"],0)
        self.assertEqual(result["missing_edges_count"],0)
        self.assertEqual(result["extra_edges_count"],1)
        self.assertEqual(result["extra_edges"],[["1","2","N",0,0]])


if __name__ == "__main__": unittest.main()
