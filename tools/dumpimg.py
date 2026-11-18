"""python dumpimg.py ARCH 정규식 → work/img/dump/<ARCH>_<name>_<i>.png (imgdata 반영본 우선)"""
import sys,os,re
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
import mvgl,gxt
from PIL import Image
a=sys.argv[1]; rx=re.compile(sys.argv[2])
base=os.path.join(D,'../work/base',a+'.psp2.mvgl')
if not os.path.exists(base): base=os.path.join(D,'../emu/fs/ux0/app/PCSG00500/CR3/resources',a+'.psp2.mvgl')
m=mvgl.MDB(base); od=os.path.join(D,'../work/img/dump'); os.makedirs(od,exist_ok=True)
for k,n,did in m.files():
    fn=n.split(chr(92))[-1]
    if not n.endswith('.img') or not rx.search(fn): continue
    sv=os.path.join(D,'../work/imgdata',a,fn)
    b=open(sv,'rb').read() if os.path.exists(sv) else m.get(did)
    for i,t in enumerate(gxt.info(b)):
        try: im=gxt.decode(b,t)
        except Exception as e: print('skip',fn,e); continue
        Image.fromarray(im).save(os.path.join(od,f'{a}_{fn[:-4]}_{i}.png')); print(fn,i,t['w'],t['h'],hex(t['fmt']))
