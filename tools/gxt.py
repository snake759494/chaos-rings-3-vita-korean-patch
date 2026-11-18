"""PS Vita GXT (UBC2/DXT3 swizzled, U8 swizzled) 디코드/인코드"""
import struct,numpy as np
def morton_idx(w,h,yfirst=True):
    """swizzle index map for w x h (in units) -> linear index list. Vita: morton within min-square, tiles along longer axis"""
    m=min(w,h); k=m.bit_length()-1
    idx=np.zeros(w*h,dtype=np.int64)
    xs=np.arange(w); ys=np.arange(h)
    X,Y=np.meshgrid(xs,ys)
    x=X%m; y=Y%m
    mort=np.zeros_like(X)
    for b in range(k):
        if yfirst:
            mort|=((y>>b)&1)<<(2*b)
            mort|=((x>>b)&1)<<(2*b+1)
        else:
            mort|=((x>>b)&1)<<(2*b)
            mort|=((y>>b)&1)<<(2*b+1)
    tile=(X//m)+(Y//m)  # one of them is 0
    sw=tile*(m*m)+mort
    return sw  # sw[y,x] = position in swizzled stream
def info(b):
    magic,ver,num,ds,dsz=struct.unpack_from('<4sIIII',b,0)
    texs=[]
    for i in range(num):
        off,size,pal,flags,ttype,fmt,w,h,mip=struct.unpack_from('<iiiIIIHHH',b,0x20+i*0x20)
        texs.append(dict(off=off,size=size,type=ttype,fmt=fmt,w=w,h=h,hdr=0x20+i*0x20))
    return texs
def _c565(c):
    r=(c>>11)&31; g=(c>>5)&63; bl=c&31
    return np.stack([(r<<3)|(r>>2),(g<<2)|(g>>4),(bl<<3)|(bl>>2)],-1).astype(np.int32)
def dxt5_blocks_decode(data,nb):
    a=np.frombuffer(data,dtype=np.uint8)[:nb*16].reshape(nb,16)
    a0=a[:,0].astype(np.int32); a1=a[:,1].astype(np.int32)
    abits=np.zeros(nb,dtype=np.uint64)
    for i in range(6): abits|=a[:,2+i].astype(np.uint64)<<np.uint64(8*i)
    al=np.zeros((nb,8),dtype=np.int32); al[:,0]=a0; al[:,1]=a1
    for i in range(1,7):
        g=a0>a1
        al[:,i+1]=np.where(g,((7-i)*a0+i*a1)//7, 0)
    for i in range(1,5):
        al[:,i+1]=np.where(a0>a1,al[:,i+1],((5-i)*a0+i*a1)//5)
    al[:,6]=np.where(a0>a1,al[:,6],0); al[:,7]=np.where(a0>a1,al[:,7],255)
    c0=a[:,8].astype(np.int32)|(a[:,9].astype(np.int32)<<8); c1=a[:,10].astype(np.int32)|(a[:,11].astype(np.int32)<<8)
    p0=_c565(c0); p1=_c565(c1)
    pal=np.stack([p0,p1,(2*p0+p1)//3,(p0+2*p1)//3],1)
    cbits=a[:,12].astype(np.uint32)|(a[:,13].astype(np.uint32)<<8)|(a[:,14].astype(np.uint32)<<16)|(a[:,15].astype(np.uint32)<<24)
    out=np.zeros((nb,16,4),dtype=np.uint8)
    for p in range(16):
        ci=(cbits>>(2*p))&3; ai=((abits>>np.uint64(3*p))&np.uint64(7)).astype(np.int64)
        out[:,p,:3]=pal[np.arange(nb),ci]
        out[:,p,3]=al[np.arange(nb),ai]
    return out
def dxt3_blocks_decode(data,nb):
    """UBC2(0x86) = DXT3: 4비트 명시 알파 + DXT1 색 블록"""
    a=np.frombuffer(data,dtype=np.uint8)[:nb*16].reshape(nb,16)
    out=dxt5_blocks_decode(data,nb)
    ab=np.zeros(nb,dtype=np.uint64)
    for i in range(8): ab|=a[:,i].astype(np.uint64)<<np.uint64(8*i)
    for p in range(16): out[:,p,3]=(((ab>>np.uint64(4*p))&np.uint64(15)).astype(np.uint8))*17
    return out
def dxt3_blocks_encode(px):
    out=np.frombuffer(dxt5_blocks_encode(px),dtype=np.uint8).reshape(-1,16).copy()
    a=(px[...,3].astype(np.int32)*15+127)//255
    ab=np.zeros(px.shape[0],dtype=np.uint64)
    for i in range(16): ab|=a[:,i].astype(np.uint64)<<np.uint64(4*i)
    for i in range(8): out[:,i]=((ab>>np.uint64(8*i))&np.uint64(255)).astype(np.uint8)
    return out.tobytes()
LEGACY_DXT5=False  # True면 예전(잘못된) DXT5 해석 — 변환용
def decode(b,t):
    w,h=t['w'],t['h']; d=b[t['off']:t['off']+t['size']]
    base=t['fmt']&0xFF000000
    if base==0x86000000:
        bw,bh=(w+3)//4,(h+3)//4
        pw=1<<(bw-1).bit_length(); ph=1<<(bh-1).bit_length()
        blocks=(dxt5_blocks_decode if LEGACY_DXT5 else dxt3_blocks_decode)(d,pw*ph)
        sw=morton_idx(pw,ph)
        img=np.zeros((ph*4,pw*4,4),dtype=np.uint8)
        bl=blocks[sw.reshape(-1)].reshape(ph,pw,4,4,4)
        img=bl.transpose(0,2,1,3,4).reshape(ph*4,pw*4,4)
        return img[:h,:w]
    elif base==0x00000000:
        pw=1<<(w-1).bit_length(); ph=1<<(h-1).bit_length()
        a=np.frombuffer(d,dtype=np.uint8)[:pw*ph]
        sw=morton_idx(pw,ph)
        v=a[sw.reshape(-1)].reshape(ph,pw)[:h,:w]
        img=np.zeros((h,w,4),dtype=np.uint8); img[...,:3]=255; img[...,3]=v
        return img
    raise ValueError(hex(t['fmt']))
def _to565(c):
    c=np.clip(c,0,255).astype(np.int32)
    return ((c[...,0]>>3)<<11)|((c[...,1]>>2)<<5)|(c[...,2]>>3)
def dxt5_blocks_encode(px):
    """px: (nb,16,4) uint8 -> bytes"""
    nb=px.shape[0]; p=px.astype(np.int32)
    out=np.zeros((nb,16),dtype=np.uint8)
    a=p[...,3]; amax=a.max(1); amin=a.min(1)
    out[:,0]=amax; out[:,1]=amin
    # 8단계 알파 (a0>a1), a0==a1 이면 전부 인덱스0
    lv=np.stack([amax,amin]+[((7-i)*amax+i*amin)//7 for i in range(1,7)],1)
    ai=np.abs(a[:,:,None]-lv[:,None,:]).argmin(2).astype(np.uint64)
    ab=np.zeros(nb,dtype=np.uint64)
    for i in range(16): ab|=ai[:,i]<<np.uint64(3*i)
    for i in range(6): out[:,2+i]=((ab>>np.uint64(8*i))&np.uint64(255)).astype(np.uint8)
    full=(amax==255)&(amin==255); out[full,2:8]=255
    zero=(amax==0); out[zero,2:8]=0
    # 색: 불투명 픽셀 가중 bbox
    w=(a>16)[...,None]
    rgb=p[...,:3]
    big=np.where(w,rgb,-1).max(1); sm=np.where(w,rgb,256).min(1)
    none=(big<0).any(1)
    big[none]=0; sm[none]=0
    c0=_to565(big); c1=_to565(sm)
    sw=c0<c1; c0,c1=np.where(sw,c1,c0),np.where(sw,c0,c1)
    eq=c0==c1
    p0=_c565(c0); p1=_c565(c1)
    pal=np.stack([p0,p1,(2*p0+p1)//3,(p0+2*p1)//3],1)
    d=((rgb[:,:,None,:]-pal[:,None,:,:])**2).sum(3)
    ci=d.argmin(2).astype(np.uint32); ci[eq]=0
    cb=np.zeros(nb,dtype=np.uint32)
    for i in range(16): cb|=ci[:,i]<<np.uint32(2*i)
    out[:,8]=c0&255; out[:,9]=c0>>8; out[:,10]=c1&255; out[:,11]=c1>>8
    for i in range(4): out[:,12+i]=(cb>>np.uint32(8*i))&255
    return out.tobytes()
def _enc_level(img,w,h,base):
    if base==0x86000000:
        bw,bh=(w+3)//4,(h+3)//4
        pw=1<<(bw-1).bit_length(); ph=1<<(bh-1).bit_length()
        full=np.zeros((ph*4,pw*4,4),dtype=np.uint8); full[:h,:w]=img
        bl=full.reshape(ph,4,pw,4,4).transpose(0,2,1,3,4).reshape(ph*pw,16,4)
        sw=morton_idx(pw,ph).reshape(-1)
        st=np.zeros_like(bl); st[sw]=bl
        return dxt3_blocks_encode(st)
    pw=1<<(w-1).bit_length(); ph=1<<(h-1).bit_length()
    full=np.zeros((ph,pw),dtype=np.uint8); full[:h,:w]=img[...,3]
    sw=morton_idx(pw,ph).reshape(-1)
    st=np.zeros(pw*ph,dtype=np.uint8); st[sw]=full.reshape(-1); return st.tobytes()
def encode(b,t,img):
    """img (h,w,4) uint8 -> 새 GXT bytes (같은 크기). 밉맵 체인이 있으면 축소본으로 모두 재생성"""
    from PIL import Image
    w,h=t['w'],t['h']; base=t['fmt']&0xFF000000; b=bytearray(b)
    pos=t['off']; end=t['off']+t['size']; cur=Image.fromarray(np.ascontiguousarray(img))
    while True:
        data=_enc_level(np.array(cur),w,h,base)
        if pos+len(data)>end: break
        b[pos:pos+len(data)]=data; pos+=len(data)
        if w<=1 and h<=1: break
        w=max(1,w//2); h=max(1,h//2)
        if end-pos<16 and base==0x86000000: break
        cur=cur.resize((w,h),Image.BOX)
    return bytes(b)
