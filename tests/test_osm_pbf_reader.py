"""A hand-authored PBF checks delta, signed-coordinate and string-table decoding."""
import json,sqlite3,struct,zlib
from lfm.scripts.osm_pbf_reader import CLASSES,collect

def test_dense_nodes_and_way_references_round_trip(tmp_path):
    b=CLASSES['Block']();b.granularity=100;b.lon_offset=1000
    b.stringtable.s.extend([b'',b'highway',b'primary'])
    d=b.primitivegroup.add().dense
    d.id.extend([100,1,1]);d.lat.extend([-260000000,0,10]);d.lon.extend([280000000,10,-5])
    w=b.primitivegroup.add().ways.add();w.id=500;w.info.version=3
    w.keys.append(1);w.vals.append(2);w.refs.extend([100,1,1])
    raw=b.SerializeToString();blob=CLASSES['Blob'](raw_size=len(raw),zlib_data=zlib.compress(raw)).SerializeToString()
    header=CLASSES['BlobHeader'](type='OSMData',datasize=len(blob)).SerializeToString()
    path=tmp_path/'test.pbf';path.write_bytes(struct.pack('>I',len(header))+header+blob)
    db=sqlite3.connect(':memory:')
    db.executescript('CREATE TABLE ways(id INTEGER PRIMARY KEY,version,mode,tags,nodes,geometry); CREATE TABLE restrictions(id PRIMARY KEY,tags,members); CREATE TABLE places(id PRIMARY KEY,tags,lon,lat,position_basis);')
    collect(path,{'primary'},db)
    wid,version,mode,tags,refs,geom=db.execute('SELECT * FROM ways').fetchone()
    assert (wid,version,mode)==(500,3,'road')
    assert json.loads(refs)==[100,101,102]
    assert json.loads(tags)=={'highway':'primary'}
    points=json.loads(geom)
    assert abs(points[0][0]-28.000001)<1e-10
    assert abs(points[0][1]+26)<1e-10
    assert abs(points[2][0]-28.0000015)<1e-10
    assert abs(points[2][1]+25.999999)<1e-10
