"""카오스링 III 한글패치 빌드
python build.py [--install]  → ../out/ 에 패치 파일 생성 (--install 이면 에뮬 app 폴더에도 복사)"""
import os,sys,json,glob,re,shutil
sys.stdout.reconfigure(encoding='utf-8')
D=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.normpath(os.path.join(D,'..'))
sys.path.insert(0,D)
import mvgl,msg,mbe,repack,bsonpatch,fontbuild,imgpatch
W=os.path.join(ROOT,'work'); BASE=os.path.join(W,'base'); OUT=os.path.join(ROOT,'out')
APP=os.path.join(ROOT,'emu/fs/ux0/app/PCSG00500/CR3/resources')
def unesc(s): return s.replace('\\N','\n').replace('\\T','\t').replace('\\r','\r')
def load_tr():
    idx=json.load(open(os.path.join(W,'tr/index.json'),encoding='utf-8'))['order']
    tr={}
    for f in sorted(glob.glob(os.path.join(W,'tr/out/b*.txt'))):
        for ln in open(f,encoding='utf-8'):
            ln=ln.rstrip('\n')
            if '\t' not in ln or ln.startswith('#'): continue
            i,s=ln.split('\t',1)
            if not i.strip().isdigit(): continue
            i=int(i)
            if i<len(idx): tr[idx[i]]=unesc(s)
    # 수정본(fix) 우선
    fx=os.path.join(W,'tr/fix.json')
    if os.path.exists(fx): tr.update(json.load(open(fx,encoding='utf-8')))
    return tr,idx
def tmsg(b,tr):
    e,t=msg.parse(b)
    e=[[tr.get(a,a),tr.get(x,x)] for a,x in e]
    return msg.build(e,t)
def tmbe(b,tr):
    h,ch=mbe.parse(b); ch2=[]
    for o,r in ch:
        s=mbe.text(r)
        ch2.append([o,mbe.enc(tr[s]) if s is not None and s in tr else r])
    return mbe.build(h,ch2)
def main():
    tr,idx=load_tr()
    print('translations',len(tr),'/',len(idx))
    os.makedirs(OUT,exist_ok=True)
    used=set()
    # CRDB
    m=mvgl.MDB(os.path.join(BASE,'CRDB.psp2.mvgl')); repl={}; nb=0
    for k,n,did in m.files():
        if n.startswith('message\\') and n.endswith('.dat'):
            repl[did]=tmsg(m.get(did),tr)
        elif n.endswith('.mbe'):
            b=m.get(did); nb2=tmbe(b,tr)
            if nb2!=b: repl[did]=nb2
        elif n.endswith('.bson') and not n.endswith('ngword.bson'):
            b=m.get(did); nb2,c=bsonpatch.patch(b,tr)
            if c: repl[did]=nb2; nb+=c
    print('CRDB files',len(repl),'bson refs',nb)
    repack.repack(m,repl,os.path.join(OUT,'CRDB.psp2.mvgl'))
    # CRDBboot
    m=mvgl.MDB(os.path.join(BASE,'CRDBboot.psp2.mvgl')); repl={}
    for k,n,did in m.files():
        if n.endswith('.dat') and not n.startswith('data'):
            repl[did]=tmsg(m.get(did),tr)
    ispec=imgpatch.load_all()
    ri=imgpatch.patch_archive(m,ispec,'CRDBboot'); repl.update(ri)
    repack.repack(m,repl,os.path.join(OUT,'CRDBboot.psp2.mvgl'))
    print('boot files',len(repl),'imgs',len(ri))
    # 이미지 전용 아카이브
    imgarch=[]
    # 카드 뷰어(HTML) 버튼
    m=mvgl.MDB(os.path.join(BASE,'CRDBcardhd.psp2.mvgl'))
    for k,n,did in m.files():
        if n=='index.html':
            repack.repack(m,{did:m.get(did).replace('閉じる'.encode(),'닫기'.encode())},os.path.join(OUT,'CRDBcardhd.psp2.mvgl'))
            imgarch.append('CRDBcardhd')
    for a in imgpatch.ARCHS:
        if a=='CRDBboot': continue
        m=mvgl.MDB(os.path.join(BASE,a+'.psp2.mvgl'))
        ri=imgpatch.patch_archive(m,ispec,a)
        if ri: repack.repack(m,ri,os.path.join(OUT,a+'.psp2.mvgl')); imgarch.append(a)
        print(a,'imgs',len(ri))
    # font: 번역문 전체 글자 + KS X 1001 한글 2350자
    for s in tr.values(): used|=set(map(ord,s))
    used|=set(ord(c) for c in open(os.path.join(W,'ks2350.txt'),encoding='utf-8').read())
    fontbuild.build(used,os.path.join(OUT,'TBGB_0KP.TTC'))
    if '--install' in sys.argv:
        shutil.copy(os.path.join(OUT,'CRDB.psp2.mvgl'),APP)
        shutil.copy(os.path.join(OUT,'CRDBboot.psp2.mvgl'),APP)
        for a in imgarch: shutil.copy(os.path.join(OUT,a+'.psp2.mvgl'),APP)
        shutil.copy(os.path.join(OUT,'TBGB_0KP.TTC'),os.path.join(APP,'font'))
        print('installed to emulator')
if __name__=='__main__': main()
