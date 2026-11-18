import struct, sys, os
def dbz_header(b):
    a=b[0]; n=((a>>3)&7)+1; stored=(a>>7)&1
    us=int.from_bytes(b[1:1+n],'little'); cs=int.from_bytes(b[1+n:1+2*n],'little')
    return us,cs,stored,1+2*n
LUT=[(0xff,2,0,0,1),(0xffff,2,0,0,2),(0xffff,6,15,2,2),(0xffffff,8,31,3,3),(0xff,2,0,0,1),(0xffff,2,0,0,2),(0xffff,6,15,2,2),(0xffffffff,11,255,3,4)]
def dbz_dec(b):
    us,cs,st,h=dbz_header(b)
    if st: return bytes(b[h:h+us])
    src=b+b'\0'*8; i=h; out=bytearray(); cw=1
    while len(out)<us:
        if cw==1:
            cw=struct.unpack_from('<I',src,i)[0]; i+=4
        if cw&1==0:
            out.append(src[i]); i+=1
        else:
            w=struct.unpack_from('<I',src,i)[0]; t=w&7; m,os_,lm,ls,sz=LUT[t]
            off=(w&m)>>os_; ln=((w>>ls)&lm)+3; i+=sz
            p=len(out)-off
            for k in range(ln): out.append(out[p+k])
        cw>>=1
    return bytes(out)
def dbz_enc(data):
    """greedy LZ doboz encoder"""
    n=len(data); out=bytearray(); ctrl_pos=None; bits=0; nb=0
    blocks=[]  # list of (flag, bytes)
    table={}; i=0
    while i<n:
        best=0; bo=0
        if i+3<=n-8:
            key=data[i:i+3]; cands=table.get(key)
            if cands:
                for p in reversed(cands[-16:]):
                    off=i-p
                    if off>=(1<<21): continue
                    l=3; mx=min(258,n-8-i)
                    if data[p:p+3]!=data[i:i+3]: continue
                    while l<mx and data[p+l]==data[i+l]: l+=1
                    if l>best: best=l; bo=off
                    if l==mx: break
        if best>=3:
            ln=best-3; off=bo
            if ln==0 and off<64: enc=struct.pack('<B',(off<<2)|0); 
            elif ln==0 and off<16384: enc=struct.pack('<H',(off<<2)|1)
            elif ln<16 and off<1024: enc=struct.pack('<H',(off<<6)|(ln<<2)|2)
            elif ln<32 and off<65536: enc=((off<<8)|(ln<<3)|3).to_bytes(3,'little')
            else:
                if off>=(1<<21): enc=None
                else: enc=struct.pack('<I',(off<<11)|(ln<<3)|7)
            blocks.append((1,enc))
            for k in range(i,i+best):
                if k+3<=n: table.setdefault(data[k:k+3],[]).append(k)
            i+=best
        else:
            blocks.append((0,data[i:i+1]))
            if i+3<=n: table.setdefault(data[i:i+3],[]).append(i)
            i+=1
    body=bytearray()
    for s in range(0,len(blocks),31):
        grp=blocks[s:s+31]; cw=0x80000000
        for j,(f,_) in enumerate(grp): cw|=f<<j
        body+=struct.pack('<I',cw)
        for _,e in grp: body+=e
    body+=b'\0'*4  # padding
    return body
def dbz_pack(data,compress=True):
    body=dbz_enc(data) if compress else None
    if body is None or len(body)>=len(data):
        stored=True; body=data
    else: stored=False
    for n in (1,2,4):
        if len(data)<(1<<(8*n)) and (1+2*n+len(body))<(1<<(8*n)): break
    tot=1+2*n+len(body)
    a=((n-1)<<3)|(0x80 if stored else 0)
    return bytes([a])+len(data).to_bytes(n,'little')+tot.to_bytes(n,'little')+body
class MDB:
    def __init__(s,path):
        s.path=path; f=open(path,'rb'); s.raw=f.read()
        d=s.raw; fe,fn,de,s.u0,ds,ts=struct.unpack_from('<4H2I',d,4)
        s.fe,s.fn,s.de,s.ds=fe,fn,de,ds
        s.tree=d[0x14:0x14+fe*8]
        o=0x14+fe*8; s.names=[]
        for k in range(fn):
            e=d[o+k*0x40:o+k*0x40+0x40]; s.names.append((e[:4].rstrip(b'\0 ').decode(),e[4:].split(b'\0')[0].decode('cp932')))
        o2=o+fn*0x40; s.data=[struct.unpack_from('<3I',d,o2+k*12) for k in range(de)]
        s.tree_entries=[struct.unpack_from('<hhHH',d,0x14+k*8) for k in range(fe)]
    def files(s):
        # map name idx -> data id via tree
        for k,(cb,did,l,r) in enumerate(s.tree_entries):
            if did>=0:
                ext,nm=s.names[k]; yield k,nm+'.'+ext,did
    def get(s,did):
        off,us,cs=s.data[did]; b=s.raw[s.ds+off:s.ds+off+cs]
        if us==cs: return b
        return dbz_dec(b)
if __name__=='__main__':
    m=MDB(sys.argv[1])
    for k,n,did in m.files():
        print(k,n,did,m.data[did])
