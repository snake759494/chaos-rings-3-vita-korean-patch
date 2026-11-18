"""imgdata(예전 DXT5로 잘못 인코딩된 수작업 GXT)를 DXT3로 변환. 바뀌지 않은 블록은 원본에서 올바르게 디코드한 픽셀 사용."""
import os, sys, glob, shutil, numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import mvgl, gxt
W = os.path.join(D, '..', 'work'); OLD = os.path.join(W, 'imgdata_old')
if not os.path.exists(OLD): shutil.copytree(os.path.join(W, 'imgdata'), OLD)
for arch in os.listdir(OLD):
    m = mvgl.MDB(os.path.join(W, 'base', arch + '.psp2.mvgl'))
    orig = {n.split('\\')[-1]: d for k, n, d in m.files()}
    for f in glob.glob(os.path.join(OLD, arch, '*.img')):
        fn = os.path.basename(f); ed = open(f, 'rb').read(); ob = m.get(orig[fn])
        out = ed
        for t in gxt.info(ed):
            if t['fmt'] & 0xFF000000 != 0x86000000: continue
            gxt.LEGACY_DXT5 = True
            e_old = gxt.decode(ed, t).astype(np.int32); o_old = gxt.decode(ob, t).astype(np.int32)
            gxt.LEGACY_DXT5 = False
            o_new = gxt.decode(ob, t)
            h, w = e_old.shape[:2]
            diff = np.abs(e_old - o_old).max(2)
            bd = diff[:h//4*4, :w//4*4].reshape(h//4, 4, w//4, 4).max((1, 3)) > 24
            mask = np.repeat(np.repeat(bd, 4, 0), 4, 1) & (diff > 24)
            px = np.where(mask[..., None], e_old, o_new).astype(np.uint8)
            px[mask & (e_old[..., 3] < 48), 3] = 0
            out = gxt.encode(out, t, px)
            print(arch, fn, 'changed blocks', int(bd.sum()))
        open(os.path.join(W, 'imgdata', arch, fn), 'wb').write(out)


