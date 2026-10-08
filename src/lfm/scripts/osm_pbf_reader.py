"""Read the published OSM PBF schema using the existing protobuf runtime.

Schema: https://github.com/openstreetmap/OSM-binary/tree/master/osmpbf
Supports ordinary/dense nodes and raw/zlib blobs; rejects unsupported compression.
"""
import json,struct,zlib
from itertools import accumulate
from google.protobuf import descriptor_pb2,descriptor_pool,message_factory

def schema():
    doc=descriptor_pb2.FileDescriptorProto(name='lfm_osm.proto',package='lfm_osm',syntax='proto2')
    def message(name,fields):
        m=doc.message_type.add(name=name)
        for number,field,kind,repeated in fields:
            f=m.field.add(name=field,number=number,label=3 if repeated else 1)
            if isinstance(kind,str):f.type=11;f.type_name='.lfm_osm.'+kind
            else:f.type=kind
            if repeated and not isinstance(kind,str) and kind not in (9,12):f.options.packed=True
    message('BlobHeader',[(1,'type',9,False),(3,'datasize',5,False)])
    message('Blob',[(1,'raw',12,False),(2,'raw_size',5,False),(3,'zlib_data',12,False)])
    message('Strings',[(1,'s',12,True)])
    message('Info',[(1,'version',5,False)])
    common=[(1,'id',3,False),(2,'keys',13,True),(3,'vals',13,True),(4,'info','Info',False)]
    message('Node',[(1,'id',18,False),*common[1:],(8,'lat',18,False),(9,'lon',18,False)])
    message('Dense',[(1,'id',18,True),(8,'lat',18,True),(9,'lon',18,True),(10,'keys_vals',5,True)])
    message('Way',common+[(8,'refs',18,True)])
    message('Relation',common+[(8,'roles_sid',5,True),(9,'memids',18,True),(10,'types',5,True)])
    message('Group',[(1,'nodes','Node',True),(2,'dense','Dense',False),(3,'ways','Way',True),(4,'relations','Relation',True)])
    message('Block',[(1,'stringtable','Strings',False),(2,'primitivegroup','Group',True),(17,'granularity',5,False),(19,'lat_offset',3,False),(20,'lon_offset',3,False)])
    pool=descriptor_pool.DescriptorPool();pool.Add(doc)
    return {n:message_factory.GetMessageClass(pool.FindMessageTypeByName('lfm_osm.'+n)) for n in ['BlobHeader','Blob','Block']}
CLASSES=schema()
def blocks(path):
    with path.open('rb') as f:
        while size:=f.read(4):
            if len(size)!=4:raise ValueError('Truncated PBF header')
            size=struct.unpack('>I',size)[0]
            if not 0<size<65536:raise ValueError('Invalid PBF header size')
            header=CLASSES['BlobHeader'].FromString(f.read(size));blob=f.read(header.datasize)
            if len(blob)!=header.datasize:raise ValueError('Truncated PBF blob')
            if header.type!='OSMData':continue
            blob=CLASSES['Blob'].FromString(blob)
            if blob.HasField('raw'):data=blob.raw
            elif blob.HasField('zlib_data'):data=zlib.decompress(blob.zlib_data)
            else:raise ValueError('Unsupported PBF compression')
            if blob.HasField('raw_size') and len(data)!=blob.raw_size:raise ValueError('PBF raw size mismatch')
            yield CLASSES['Block'].FromString(data)
def tags(obj,strings):return {strings[k]:strings[v] for k,v in zip(obj.keys,obj.vals)}
def relevant(t):return t.get('barrier')=='border_control' or any(x in t.get('name','').lower() for x in ['vopak','natref','secunda'])
def collect(path,highways,db):
    selected=[];needed=set()
    for block in blocks(path):
        strings=[s.decode('utf-8') for s in block.stringtable.s]
        for group in block.primitivegroup:
            for w in group.ways:
                t=tags(w,strings)
                mode='road' if t.get('highway') in highways else 'rail' if t.get('railway')=='rail' else 'pipeline' if t.get('man_made')=='pipeline' else None
                if not mode and not relevant(t):continue
                refs=list(accumulate(w.refs));needed.update(refs)
                selected.append((w.id,w.info.version,mode,t,refs))
            for r in group.relations:
                t=tags(r,strings)
                if t.get('type')=='restriction':
                    members=[(['n','w','r'][kind],ref,strings[role]) for kind,ref,role in zip(r.types,accumulate(r.memids),r.roles_sid)]
                    db.execute('INSERT OR IGNORE INTO restrictions VALUES(?,?,?)',(r.id,json.dumps(t),json.dumps(members)))
    print(path.stem,'selected ways',len(selected),'required nodes',len(needed),flush=True)
    coords={}
    for block in blocks(path):
        strings=[s.decode('utf-8') for s in block.stringtable.s]
        gran=block.granularity if block.HasField('granularity') else 100
        la,lo=block.lat_offset,block.lon_offset
        scan_tags=any(any(x in s.lower() for x in ['vopak','natref','secunda','border_control']) for s in strings)
        def point(nid,lat,lon,t=None):
            p=((lo+gran*lon)*1e-9,(la+gran*lat)*1e-9)
            if nid in needed:coords[nid]=p
            if t and relevant(t):db.execute('INSERT OR IGNORE INTO places VALUES(?,?,?,?,?)',(f'node/{nid}',json.dumps(t),*p,'OSM node; entrance unverified'))
        for group in block.primitivegroup:
            for n in group.nodes:
                if n.id in needed or scan_tags:point(n.id,n.lat,n.lon,tags(n,strings) if scan_tags else None)
            if group.HasField('dense'):
                d=group.dense;k=0;kv=d.keys_vals
                for nid,lat,lon in zip(accumulate(d.id),accumulate(d.lat),accumulate(d.lon)):
                    t=None
                    if scan_tags and kv:
                        t={}
                        while kv[k]:t[strings[kv[k]]]=strings[kv[k+1]];k+=2
                        k+=1
                    if nid in needed or t:point(nid,lat,lon,t)
    missing=needed-coords.keys()
    if missing:raise ValueError(f'{path.name}: {len(missing)} referenced nodes absent')
    for wid,version,mode,t,refs in selected:
        geometry=[coords[n] for n in refs]
        if len(geometry)<2:continue
        if relevant(t):db.execute('INSERT OR IGNORE INTO places VALUES(?,?,?,?,?)',(f'way/{wid}',json.dumps(t),sum(p[0] for p in geometry)/len(geometry),sum(p[1] for p in geometry)/len(geometry),'vertex mean of OSM way; not an entrance'))
        if mode:db.execute('INSERT INTO ways VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,mode=excluded.mode,tags=excluded.tags,nodes=excluded.nodes,geometry=excluded.geometry WHERE excluded.version>ways.version',(wid,version,mode,json.dumps(t),json.dumps(refs),json.dumps(geometry)))
    db.commit()
