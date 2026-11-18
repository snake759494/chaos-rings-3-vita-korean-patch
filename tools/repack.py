import struct,mvgl
def repack(m,repl,out):
    """m: MDB, repl: {dataid: newbytes}"""
    d=m.raw; hdr_end=m.ds
    order=sorted(range(m.de),key=lambda i:m.data[i][0])
    body=bytearray(); newdata=list(m.data)
    for i in order:
        off,us,cs=m.data[i]
        if i in repl:
            b=repl[i]; c=mvgl.dbz_pack(b)
            if c[0]&0x80 or len(c)>=len(b):  # stored, 또는 압축 크기>=원본 → raw (us==cs) 로 저장
                c=b
            newdata[i]=(len(body),len(b),len(c)); body+=c
        else:
            newdata[i]=(len(body),us,cs); body+=d[m.ds+off:m.ds+off+cs]
    h=bytearray(d[:hdr_end])
    o2=0x14+m.fe*8+m.fn*0x40
    for i,(a,b,c) in enumerate(newdata): struct.pack_into('<3I',h,o2+i*12,a,b,c)
    struct.pack_into('<I',h,0x10,len(h)+len(body))
    with open(out,'wb') as f: f.write(h); f.write(body)
