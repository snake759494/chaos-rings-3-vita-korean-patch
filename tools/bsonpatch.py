"""Media.Vision BSON: 문자열 참조 레코드 (u16 0x14, u16 0x0c, u32 key, u32 val) 의 val 을 새 문자열로 교체.
새 문자열은 파일 끝에 덧붙이고 풀 기준 오프셋으로 가리킨다."""
import struct,re
def refs(d):
    out=[]
    for m in re.finditer(rb'\x14\x00\x0c\x00',d):
        p=m.start()
        if p%4==0 and p+12<=len(d):
            k,v=struct.unpack_from('<2I',d,p+4); out.append((p,k,v))
    return out
def pool_start(d,rs):
    vals=set()
    for p,k,v in rs: vals.add(k); vals.add(v)
    vals=sorted(vals)
    lo=max(p for p,k,v in rs)+12
    for P in range(lo,len(d)):
        ok=True
        for v in vals:
            q=P+v
            if q>=len(d) or (v>0 and d[q-1]!=0): ok=False; break
        if ok: return P
    raise ValueError('pool not found')
def cstr(d,o):
    e=d.index(b'\0',o); return d[o:e]
def patch(d,tr):
    rs=refs(d)
    if not rs: return d,0
    try: P=pool_start(d,rs)
    except ValueError: return d,0
    out=bytearray(d); added={}; n=0
    for p,k,v in rs:
        try: s=cstr(d,P+v).decode('utf-8')
        except Exception: continue
        if s in tr and tr[s]!=s:
            t=tr[s]
            if t not in added:
                added[t]=len(out)-P; out+=t.encode('utf-8')+b'\0'
            struct.pack_into('<I',out,p+8,added[t]); n+=1
    while len(out)%4: out+=b'\0'
    return bytes(out),n
