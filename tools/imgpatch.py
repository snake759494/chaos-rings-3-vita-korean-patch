"""UI 이미지 글자 교체. spec: work/img/spec.json
{ "CRDBboot": { "images\\bt_parts_01.img": [ {"tex":0,"box":[x0,y0,x1,y1],"text":"..","size":22,
   "fill":[255,255,255],"stroke":[0,0,80],"sw":2,"erase":"row"|"clear"|"none","align":"l|c|r","font":"nanum|galmuri"} ] } }
erase=row : 박스 각 행을 좌우 가장자리 색의 선형보간으로 채움(그라데이션 버튼용)
erase=clear: 투명으로 지움
rot: 90(반시계)/270(시계) 회전 글자"""
import json,os,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
D=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.normpath(os.path.join(D,'..'))
sys.path.insert(0,D)
import gxt
FONTS={'nanum':os.path.join(ROOT,'NanumSquareNeo-dEb.ttf'),'nanumb':os.path.join(ROOT,'NanumSquareNeo-cBd.ttf'),
       'galmuri':os.path.join(ROOT,'work','Galmuri11-Bold.ttf'),'galmuri9':os.path.join(ROOT,'work','Galmuri9.ttf')}
def erase_row(a,x0,y0,x1,y1):
    L=a[y0:y1,max(x0-1,0)].astype(float); R=a[y0:y1,min(x1,a.shape[1]-1)].astype(float)
    n=x1-x0
    for i in range(n):
        f=(i+0.5)/n; a[y0:y1,x0+i]=(L*(1-f)+R*f).astype(np.uint8)
def render(img,e):
    a=np.array(img); x0,y0,x1,y1=e['box']
    m=e.get('erase','row')
    if m=='row': erase_row(a,x0,y0,x1,y1)
    elif m=='clear': a[y0:y1,x0:x1]=0
    im=Image.fromarray(a)
    if not e.get('text'): return im
    size=e.get('size',20); sw=e.get('sw',0)
    fp=FONTS[e.get('font','nanum')]
    W=x1-x0; H=y1-y0; rot=e.get('rot',0)
    if rot in (90,270): W,H=H,W
    while True:
        f=ImageFont.truetype(fp,size)
        bb=f.getbbox(e['text'],stroke_width=sw)
        tw=bb[2]-bb[0]; th=bb[3]-bb[1]
        if tw<=W or size<=8: break
        size-=1
    # 가로 압축이 필요하면 별도 레이어에 그린 뒤 축소
    lay=Image.new('RGBA',(max(tw,1)+4,th+4),(0,0,0,0))
    ImageDraw.Draw(lay).text((2-bb[0],2-bb[1]),e['text'],font=f,fill=tuple(e.get('fill',[255,255,255]))+(255,),
        stroke_width=sw,stroke_fill=tuple(e.get('stroke',[0,0,0]))+(255,))
    if lay.width>W: lay=lay.resize((W,lay.height),Image.LANCZOS)
    if rot: lay=lay.rotate(rot,expand=True,resample=Image.BICUBIC); W,H=x1-x0,y1-y0
    al=e.get('align','c')
    px=x0 if al=='l' else (x1-lay.width if al=='r' else x0+(W-lay.width)//2)
    py=y0+(H-lay.height)//2+e.get('dy',0)
    im.alpha_composite(lay,(px+e.get('dx',0),py))
    return im
def patch_archive(m,spec,arch=None):
    """m: MDB, spec: {name:[entries]} -> {did: newbytes}
    arch 지정 시 work/imgdata/<arch>/<파일명> (이미 한글화된 GXT)를 바탕으로 사용"""
    repl={}
    ID=os.path.join(ROOT,'work/imgdata',arch) if arch else None
    for k,n,did in m.files():
        n2=n.replace(chr(92),"/"); fn=n2.split('/')[-1]
        saved=os.path.join(ID,fn) if ID else None
        has=saved and os.path.exists(saved)
        if n2 not in spec and not has: continue
        n=n2
        b=open(saved,'rb').read() if has else m.get(did)
        if n not in spec: repl[did]=b; continue
        ts=gxt.info(b)
        for ti in sorted(set(e.get('tex',0) for e in spec[n])):
            t=ts[ti]; im=Image.fromarray(gxt.decode(b,t)).convert('RGBA')
            for e in spec[n]:
                if e.get('tex',0)==ti: im=render(im,e)
            b=gxt.encode(b,t,np.array(im))
        repl[did]=b
    return repl
ARCHS=['CRDBboot','CRDBui01','CRDBadv01','CRDBbundle']
def load_all():
    """work/img/spec*.json 전부 병합 → {name:[entries]} (name 예: images/bt_parts_01.img)"""
    import glob
    out={}
    for f in sorted(glob.glob(os.path.join(ROOT,'work/img/spec_*.json'))):
        try: d=json.load(open(f,encoding='utf-8'))
        except Exception as ex: print('spec 오류',f,ex); continue
        for n,es in d.items(): out.setdefault(n,[]).extend(es)
    return out
if __name__=='__main__':
    # 미리보기: python imgpatch.py SPECFILE.json [이미지이름 일부]  → work/img/prev/<arch>_<name>_<tex>.png
    import mvgl
    spec=json.load(open(sys.argv[1],encoding='utf-8'))
    if len(sys.argv)>2: spec={k:v for k,v in spec.items() if sys.argv[2] in k}
    od=os.path.join(ROOT,'work/img/prev'); os.makedirs(od,exist_ok=True)
    for arch in ARCHS:
        m=mvgl.MDB(os.path.join(ROOT,'work/base',arch+'.psp2.mvgl'))
        r=patch_archive(m,spec,arch); r={k:v for k,v in r.items() if any(n.replace(chr(92),'/') in spec for kk,n,dd in m.files() if dd==k)}
        for k,n,did in m.files():
            if did in r:
                for i,t in enumerate(gxt.info(r[did])):
                    fn=os.path.join(od,arch+'_'+n.split(chr(92))[-1][:-4]+f'_{i}.png')
                    Image.fromarray(gxt.decode(r[did],t)).save(fn); print(fn)
