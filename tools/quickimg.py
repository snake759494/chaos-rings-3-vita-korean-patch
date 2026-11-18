"""이미지 아카이브만 빠르게 재생성해 에뮬에 설치: python quickimg.py ARCH [이름필터]"""
import sys,os,json
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
import mvgl,repack,imgpatch
a=sys.argv[1]; flt=sys.argv[2] if len(sys.argv)>2 else ''
spec=imgpatch.load_all()
m=mvgl.MDB(os.path.join(D,'../work/base',a+'.psp2.mvgl'))
ri=imgpatch.patch_archive(m,spec,a)
if flt:
    keep={d for k,n,d in m.files() if flt in n}
    ri={k:v for k,v in ri.items() if k in keep}
out=os.path.join(D,'../emu/fs/ux0/app/PCSG00500/CR3/resources',a+'.psp2.mvgl')
repack.repack(m,ri,out); print(a,len(ri))
