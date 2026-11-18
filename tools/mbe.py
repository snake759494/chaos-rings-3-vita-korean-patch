import struct
def parse(d):
    """returns head, list of [fileoffset, rawbytes]"""
    assert d[:4]==b'EXPA'
    p=d.find(b'CHNK'); assert p>0
    n=struct.unpack_from('<I',d,p+4)[0]; o=p+8; ch=[]
    for i in range(n):
        off,sz=struct.unpack_from('<2I',d,o); ch.append([off,d[o+8:o+8+sz]]); o+=8+sz
    assert o==len(d),(o,len(d))
    return d[:p],ch
def text(raw):
    e=raw.find(b'\0')
    if e<0: return None
    try: return raw[:e].decode('utf-8')
    except UnicodeDecodeError: return None
def enc(s):
    b=s.encode('utf-8'); n=(len(b)+2+3)//4*4
    return b+b'\0'*(n-len(b))
def build(head,ch):
    out=bytearray(head)+b'CHNK'+struct.pack('<I',len(ch))
    for off,raw in ch:
        out+=struct.pack('<2I',off,len(raw))+raw
    return bytes(out)
