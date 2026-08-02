#!/usr/bin/env python3
"""Create the Phase 1 raw/provisional semantic baseline from immutable SQLite files."""
from __future__ import annotations

import argparse, hashlib, json, os, sqlite3, struct, tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "baseline.sql"
DEFAULT_CONFIG = ROOT / "config" / "source_paths.local.json"
DEFAULT_DB = ROOT / "var" / "baseline" / "rose-baseline.sqlite"
DEFAULT_REPORT = ROOT / "var" / "reports" / "baseline-import.json"
DIRECTIONS = ("N","S","E","W","NW","NE","SE","SW","U","D")
NO_TARGET = {0, 0x7fffffff, 0xffffffff}
KNOWN_TAGS = {0x0A:"room",0x0D:"door",0x28:"npc",0x30:"spawn",0x32:"item"}
TAG_OFFSET = 8
ATTR_MAP = {0:"strength",1:"wisdom",2:"dexterity",3:"constitution",4:"intelligence",5:"charisma",6:"comeliness",7:"perception"}
SKILL_MAP = {
    0:"melee",1:"empty hand combat",2:"BOWMAN",3:"ARMOR",4:"DODGE",5:"MAGDEFEN",
    6:"Shpere of life",7:"Sphere of Forces",8:"sphere of body",9:"sphere of alchamey",
    10:"Sphere of Correspondence",11:"Herpitology",12:"Vitonecrology",13:"cornicology",
    14:"Horticulture",15:"Divination",16:"Linguistics",17:"Hunting",18:"natural healing",
    19:"Herbalism",20:"Mountaineering",21:"Reparations",22:"Minor thieving",
    23:"Major thieving",24:"Acquisitioning",25:"Climbing",26:"GOBLIN",
    27:"destramantology",28:"cornicology",29:"Sphere of Necromancy",41:"Move Silently",
    42:"Climb Wall",43:"BackStab",44:"PICKLOCK",45:"Traps",
}

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def qident(name: str) -> str: return '"'+name.replace('"','""')+'"'
def ro_connect(path: Path) -> sqlite3.Connection:
    uri=path.resolve().as_uri()+"?mode=ro&immutable=1"
    c=sqlite3.connect(uri,uri=True); c.row_factory=sqlite3.Row
    c.execute("PRAGMA query_only=ON")
    return c

def configured(config: Path) -> tuple[list[Path],Path|None]:
    data=json.loads(config.read_text(encoding="utf-8")); dbs=[]; graph=None
    for s in data["sources"]:
        p=Path(os.path.expandvars(s["path"])).expanduser()
        if s["name"]=="sqlite_databases": dbs=sorted(p.glob("*.db"),key=lambda x:x.name.casefold())
        elif s["name"]=="derived_graph": graph=p
    if not dbs: raise ValueError("No configured SQLite databases")
    return [p.resolve(strict=True) for p in dbs], graph.resolve(strict=True) if graph else None

def canonical_value(v: Any) -> tuple[str,bytes]:
    if v is None: return "null",b"N"
    if isinstance(v,bytes): return "blob",b"B"+len(v).to_bytes(8,"big")+v
    if isinstance(v,int): return "integer",b"I"+str(v).encode()
    if isinstance(v,float): return "real",b"R"+v.hex().encode()
    b=str(v).encode("utf-8"); return "text",b"T"+len(b).to_bytes(8,"big")+b

def value_bytes(v: Any) -> bytes:
    if v is None: return b""
    if isinstance(v,bytes): return v
    if isinstance(v,float): return v.hex().encode("ascii")
    return str(v).encode("utf-8")

def decode_text(raw: bytes) -> str:
    # CP437 is the DOS-era source encoding assumption; it decodes every byte.
    return raw.split(b"\0",1)[0].decode("cp437").strip()

def decode_quest_text(raw: bytes) -> str:
    return " ... ".join(part.decode("cp437").strip() for part in raw.split(b"\0") if part.decode("cp437").strip())

def u32(blob: bytes, off: int) -> int|None:
    return struct.unpack_from("<I",blob,off)[0] if len(blob)>=off+4 else None

def parse_links(blob: bytes) -> list[tuple[str,int,int,int]]:
    """Return direction,target,ordinal-byte-offset,target-byte-offset.

    Assumption ported from 02_secondrealtry.py: ordinal direction bytes are
    at 170..179 and packed u32 targets at 30 onward. Truncation is retained
    raw and simply yields no unsupported decoded value.
    """
    if len(blob)<171: return []
    ords=[(i,v) for i,v in enumerate(blob[170:180]) if 1<=v<=10]
    out=[]
    for slot,(direction_index,ordinal) in enumerate(ords[:10]):
        off=30+slot*4; target=u32(blob,off)
        if target is not None and target not in NO_TARGET: out.append((DIRECTIONS[ordinal-1],target,170+direction_index,off))
    return out

def identity(columns: list[sqlite3.Row], row: sqlite3.Row, ordinal: int) -> str:
    keys=[c[1] for c in columns if c[5] or str(c[1]).startswith("key_")]
    obj={k:({"blob_sha256":hashlib.sha256(row[k]).hexdigest()} if isinstance(row[k],bytes) else row[k]) for k in keys}; obj["source_ordinal"]=ordinal
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def add_field(dst: sqlite3.Connection,eid:int,source_row_id:int,name:str,value:Any,off:int|None,width:int|None,rule:str,confidence:str):
    dst.execute("INSERT INTO decoded_field(decoded_entity_id,source_row_id,field_name,value_json,byte_offset,byte_width,decoding_rule,confidence) VALUES(?,?,?,?,?,?,?,?)",
      (eid,source_row_id,name,json.dumps(value,ensure_ascii=False,separators=(",",":")),off,width,rule,confidence))

def import_all(paths:list[Path], output:Path) -> dict[str,Any]:
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmpname=tempfile.mkstemp(prefix=output.name+".",suffix=".tmp",dir=output.parent); os.close(fd); tmp=Path(tmpname)
    totals=Counter(); tag_counts=Counter(); truncated=0; mod_rows=[]; des=defaultdict(list)
    try:
      dst=sqlite3.connect(tmp); dst.executescript(SCHEMA.read_text(encoding="utf-8"))
      dst.execute("PRAGMA journal_mode=DELETE"); dst.execute("PRAGMA synchronous=FULL")
      for file_id,path in enumerate(paths,1):
        file_hash=sha256_file(path)
        dst.execute("INSERT INTO source_file VALUES(?,?,?,?,?)",(file_id,path.stem,path.name,path.stat().st_size,file_hash))
        src=ro_connect(path)
        try:
          objects=src.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name,tbl_name").fetchall()
          for obj in objects: dst.execute("INSERT INTO schema_object(source_file_id,object_type,object_name,table_name,sql_text) VALUES(?,?,?,?,?)",(file_id,*obj))
          tables=sorted((o[1] for o in objects if o[0]=="table"),key=str.casefold)
          for table in tables:
            cols=src.execute(f"PRAGMA table_info({qident(table)})").fetchall(); names=[c[1] for c in cols]
            order="rowid" if any(c[5] for c in cols) else ",".join(qident(n) for n in names)
            for ordinal,row in enumerate(src.execute(f"SELECT * FROM {qident(table)} ORDER BY {order}"),1):
              enc=[canonical_value(row[n]) for n in names]; rh=hashlib.sha256(b"".join(x[1] for x in enc)).hexdigest()
              cur=dst.execute("INSERT INTO source_row(source_file_id,table_name,source_ordinal,source_identity_json,record_sha256) VALUES(?,?,?,?,?)",(file_id,table,ordinal,identity(cols,row,ordinal),rh)); rid=cur.lastrowid; totals["rows"]+=1
              for ci,(n,(kind,raw)) in enumerate(zip(names,enc)):
                v=row[n]; vals={"integer":(v,None,None,None),"real":(None,v,None,None),"text":(None,None,v,None),"blob":(None,None,None,v),"null":(None,None,None,None)}[kind]
                byte_length=(len(v) if isinstance(v,bytes) else len(v.encode("utf-8")) if isinstance(v,str) else None)
                dst.execute("INSERT INTO source_value(source_row_id,column_ordinal,column_name,storage_class,integer_value,real_value,text_value,blob_value,byte_length,value_sha256) VALUES(?,?,?,?,?,?,?,?,?,?)",(rid,ci,n,kind,*vals,byte_length,hashlib.sha256(value_bytes(v)).hexdigest())); totals["values"]+=1
              if table=="data_t" and "data" in names and isinstance(row["data"],bytes):
                blob=row["data"]
                if path.stem=="RCI_MOD1":
                  if len(blob)<=TAG_OFFSET: tag_counts[None]+=1; truncated+=1
                  else: tag_counts[blob[TAG_OFFSET]]+=1
                  mod_rows.append((rid,row["key_0"] if "key_0" in names else None,blob))
                elif path.stem=="RCI_DES1":
                  did=u32(blob,0)
                  if did is not None: des[did].append((rid,decode_text(blob[4:].lstrip(b"\0"))))
        finally:
          src.close()
      # DES1 descriptions: decoded but full text stays only in ignored SQLite.
      for did,candidates in sorted(des.items()):
       for rid,text in candidates:
        cur=dst.execute("INSERT INTO decoded_entity(entity_type,stable_id,source_row_id) VALUES('description',?,?)",(f"description:{did}",rid)); eid=cur.lastrowid
        add_field(dst,eid,rid,"description_id",did,0,4,"little-endian u32", "strong")
        add_field(dst,eid,rid,"text",text,4,None,"NUL-trimmed CP437 after leading NUL bytes","tentative")
      known_ids={0x32:set(),0x28:set()}
      for rid,key,blob in mod_rows:
        if len(blob)>8 and blob[8] in known_ids and (v:=u32(blob,0)) is not None: known_ids[blob[8]].add(v)
      hidden_by_key=defaultdict(dict); tags_by_key=defaultdict(list); mod_blob_by_rid={}
      for rid,key,blob in mod_rows:
        if len(blob)>8:
          mod_blob_by_rid[rid]=blob
          tags_by_key[key].append((rid,blob[8]))
          if 0xA6<=blob[8]<=0xAF: hidden_by_key[key][DIRECTIONS[blob[8]-0xA6]]=rid
      for rid,key,blob in mod_rows:
        if len(blob)<=8: continue
        tag=blob[8]; et=KNOWN_TAGS.get(tag)
        if not et: continue
        obj=u32(blob,0)
        if obj is None: continue
        cur=dst.execute("INSERT INTO decoded_entity(entity_type,stable_id,source_row_id) VALUES(?,?,?)",(et,f"{et}:{obj}",rid)); eid=cur.lastrowid
        add_field(dst,eid,rid,f"{et}_id",obj,0,4,"little-endian u32","strong")
        if len(blob)>70: add_field(dst,eid,rid,"short_description",decode_text(blob[70:120]),70,min(50,len(blob)-70),"NUL-trimmed CP437 fixed field","tentative")
        for candidate_index,(desc_rid,long_text) in enumerate(des.get(obj,()),1):
          field_name="long_description" if candidate_index==1 else f"long_description_candidate_{candidate_index}"
          add_field(dst,eid,desc_rid,field_name,long_text,4,None,"DES1 id join; NUL-trimmed CP437","tentative")
        related=tags_by_key[key]
        if et=="item":
          for cat_tag,cat_name in ((0x33,"weapon"),(0x34,"armor"),(0xCC,"potion")):
            matches=[rr for rr,t in related if t==cat_tag]
            for match_index,modifier_rid in enumerate(matches,1):
              suffix="" if match_index==1 else f"_{match_index}"
              add_field(dst,eid,modifier_rid,f"category_{cat_name}{suffix}",True,8,1,f"presence of MOD1 modifier tag 0x{cat_tag:02X} sharing key_0","tentative")
        if et=="room":
          flag_tags={0x37:"store",0x6D:"peaceful",0x6E:"spell_trainer",0x72:"tavern",0xC5:"quest",0xE0:"trap"}
          for flag_tag,flag_name in flag_tags.items():
            matches=[rr for rr,t in related if t==flag_tag]
            if matches: add_field(dst,eid,matches[0],f"is_{flag_name}",True,8,1,f"presence of MOD1 tag 0x{flag_tag:02X} sharing key_0","tentative")
          for modifier_rid,modifier_tag in related:
            modifier_blob=mod_blob_by_rid[modifier_rid]
            if modifier_tag in (0x85,0x48):
              prefix="attribute" if modifier_tag==0x85 else "skill"
              code_map=ATTR_MAP if modifier_tag==0x85 else SKILL_MAP
              if len(modifier_blob)>70:
                code=modifier_blob[70]; add_field(dst,eid,modifier_rid,f"{prefix}_code",code,70,1,"unsigned byte", "tentative")
                add_field(dst,eid,modifier_rid,f"{prefix}_name",code_map.get(code),70,1,f"legacy {prefix} code map lookup; null means unknown code","tentative")
              if len(modifier_blob)>71: add_field(dst,eid,modifier_rid,f"{prefix}_max",modifier_blob[71],71,1,"unsigned byte","tentative")
              if len(modifier_blob)>72: add_field(dst,eid,modifier_rid,f"{prefix}_min",modifier_blob[72],72,1,"unsigned byte","tentative")
            elif modifier_tag==0x75 and len(modifier_blob)>10:
              add_field(dst,eid,modifier_rid,"promotion_max",modifier_blob[10],10,1,"unsigned byte","tentative")
            elif modifier_tag==0x6E and len(modifier_blob)>220:
              add_field(dst,eid,modifier_rid,"spells_count",modifier_blob[220],220,1,"unsigned byte","tentative")
            elif modifier_tag==0xC5 and len(modifier_blob)>70:
              add_field(dst,eid,modifier_rid,"quest_text",decode_quest_text(modifier_blob[70:]),70,len(modifier_blob)-70,"CP437 NUL segments, stripped and joined with ' ... '","tentative")
        if et in ("room","door"):
          for d,target,doff,toff in parse_links(blob):
            hidden_rid=hidden_by_key[key].get(d); dst.execute("INSERT OR IGNORE INTO topology_edge(from_room,direction,to_room,door,hidden,direction_offset,target_offset,hidden_source_row_id,source_row_id) VALUES(?,?,?,?,?,?,?,?,?)",(obj,d,target,int(et=="door"),int(hidden_rid is not None),doff,toff,hidden_rid,rid))
        if et=="spawn" and len(blob)>221:
          count=min(blob[221],8); add_field(dst,eid,rid,"spawn_count",blob[221],221,1,"unsigned byte; capped at 8 entries for decoding","tentative")
          entries=[]
          for i in range(count):
            sid=int.from_bytes(blob[10+i*2:12+i*2],"little") if len(blob)>=12+i*2 else None
            qty=blob[70+i] if len(blob)>70+i else None
            typ="npc" if sid in known_ids[0x28] else "item" if sid in known_ids[0x32] else "unknown"
            entries.append({"id":sid,"count":qty,"type":typ})
            if sid is not None: add_field(dst,eid,rid,f"spawn_{i+1}_id",sid,10+i*2,2,"little-endian u16","tentative")
            if qty is not None: add_field(dst,eid,rid,f"spawn_{i+1}_count",qty,70+i,1,"unsigned byte","tentative")
            add_field(dst,eid,rid,f"spawn_{i+1}_type",typ,10+i*2,2,"membership in decoded NPC/item id sets","tentative")
      for tag,count in sorted(tag_counts.items(),key=lambda x:(x[0] is None,x[0] or 0)):
        dst.execute("INSERT INTO mod1_tag_catalog VALUES(?,?,?,?,?)",(tag,(f"0x{tag:02X}" if tag is not None else None),count,(count if tag is None else 0),TAG_OFFSET))
      # Deterministic semantic digest excludes database page representation and itself.
      digest=hashlib.sha256()
      for table in ("source_file","schema_object","source_row","source_value","decoded_entity","decoded_field","topology_edge","mod1_tag_catalog"):
        for row in dst.execute(f"SELECT * FROM {table} ORDER BY rowid"):
          digest.update(canonical_value(table)[1]); [digest.update(canonical_value(v)[1]) for v in row]
      semantic=digest.hexdigest()
      dst.execute("INSERT INTO import_run VALUES(1,1,?,?,?,?)",(semantic,len(paths),totals["rows"],totals["values"]))
      dst.commit(); ok=dst.execute("PRAGMA integrity_check").fetchone()[0];
      if ok!="ok": raise RuntimeError(ok)
      dst.execute("VACUUM"); dst.close(); os.replace(tmp,output)
      catalog=[{"tag":tag,"tag_hex":(f"0x{tag:02X}" if tag is not None else None),"record_count":count,"truncated_count":(count if tag is None else 0)} for tag,count in sorted(tag_counts.items(),key=lambda x:(x[0] is None,x[0] or 0))]
      return {"source_count":len(paths),"row_count":totals["rows"],"value_count":totals["values"],"mod1_tag_offset":TAG_OFFSET,"mod1_tag_count":len(tag_counts),"truncated_mod1_records":truncated,"mod1_tag_catalog":catalog,"semantic_sha256":semantic,"output_sha256":sha256_file(output)}
    except Exception:
      try: dst.close()
      except Exception: pass
      tmp.unlink(missing_ok=True); raise

def reconcile(db:Path,graph_path:Path|None)->dict[str,Any]:
    if not graph_path: return {"available":False}
    c=sqlite3.connect(db)
    try:
      rooms={str(r[0].split(":",1)[1]) for r in c.execute("SELECT DISTINCT stable_id FROM decoded_entity WHERE entity_type='room'")}
      edges={(str(a),str(b),d,int(door),int(hidden)) for a,d,b,door,hidden in c.execute("SELECT from_room,direction,to_room,door,hidden FROM topology_edge")}
    finally:
      c.close()
    g=json.loads(graph_path.read_text(encoding="utf-8-sig")); gn={str(n["id"]) for n in g["nodes"]}; ge={(str(e["source"]),str(e["target"]),str(e["dir"]),int(bool(e.get("door"))),int(bool(e.get("hidden")))) for e in g["edges"]}
    def exact(s): return [list(x) if isinstance(x,tuple) else x for x in sorted(s)]
    return {"available":True,"generated_nodes":len(rooms),"graph_nodes":len(gn),"missing_nodes_count":len(gn-rooms),"extra_nodes_count":len(rooms-gn),"missing_nodes":exact(gn-rooms),"extra_nodes":exact(rooms-gn),"generated_edges":len(edges),"graph_edges":len(ge),"missing_edges_count":len(ge-edges),"extra_edges_count":len(edges-ge),"missing_edges":exact(ge-edges),"extra_edges":exact(edges-ge)}

def main(argv:Iterable[str]|None=None)->int:
    p=argparse.ArgumentParser(); p.add_argument("--config",type=Path,default=DEFAULT_CONFIG); p.add_argument("--output",type=Path,default=DEFAULT_DB); p.add_argument("--report",type=Path,default=DEFAULT_REPORT); a=p.parse_args(argv)
    paths,graph=configured(a.config); before={str(x):sha256_file(x) for x in paths}; result=import_all(paths,a.output); after={str(x):sha256_file(x) for x in paths}
    if before!=after: raise RuntimeError("A source database changed during import")
    result["source_hashes_unchanged"]=True; result["reconciliation"]=reconcile(a.output,graph)
    a.report.parent.mkdir(parents=True,exist_ok=True); payload=json.dumps(result,indent=2,sort_keys=True)+"\n"; fd,n=tempfile.mkstemp(dir=a.report.parent,prefix=a.report.name); os.close(fd); Path(n).write_text(payload,encoding="utf-8"); os.replace(n,a.report)
    print(json.dumps(result,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
