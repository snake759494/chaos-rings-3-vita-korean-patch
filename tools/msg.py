import struct
def cstr(d,o):
    e=d.index(b'\0',o); return d[o:e].decode('utf-8')
def parse(d):
    h,te,cnt,z=struct.unpack_from('<4I',d,0); assert h==0x10 and z==0 and te==0x10+cnt*8,(h,te,cnt)
    ents=[]; end=te
    for i in range(cnt):
        a,b=struct.unpack_from('<2I',d,0x10+i*8)
        sa=cstr(d,te+a); sb=cstr(d,te+b); ents.append([sa,sb])
        for o,s in ((a,sa),(b,sb)): end=max(end,te+o+len(s.encode())+1)
    end=(end+3)&~3
    return ents,d[end:]
def build(ents,tail):
    cnt=len(ents); te=0x10+cnt*8; tab=bytearray(); pool=bytearray()
    for sa,sb in ents:
        offs=[]
        for s in (sa,sb):
            offs.append(len(pool)); pool+=s.encode('utf-8')+b'\0'
            while len(pool)%4: pool+=b'\0'
        tab+=struct.pack('<2I',*offs)
    return struct.pack('<4I',0x10,te,cnt,0)+tab+pool+tail
