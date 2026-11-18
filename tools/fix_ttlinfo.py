"""ttl_info/ttl_infoa: 원본(DXT3 올바른 디코드)에서 「タッチしてください」를 지우고 「터치해 주세요」를 그려 imgdata에 저장"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import mvgl, gxt
R = os.path.join(D, '..'); FONT = os.path.join(R, 'NanumSquareNeo-dEb.ttf')
BOX = (150, 350, 372, 396); TXT = '터치해 주세요'; CX, CY = 256, 372
def textlayer(size=26):
    L = Image.new('L', (512, 512), 0); d = ImageDraw.Draw(L)
    f = ImageFont.truetype(FONT, size); d.text((CX, CY), TXT, font=f, fill=255, anchor='mm'); return L
for arch in ('CRDBboot', 'CRDBui01'):
    m = mvgl.MDB(os.path.join(R, 'work/base', arch + '.psp2.mvgl'))
    for k, n, did in m.files():
        fn = n.split('\\')[-1]
        if fn not in ('ttl_info.img', 'ttl_infoa.img'): continue
        b = m.get(did); t = gxt.info(b)[0]; im = gxt.decode(b, t).copy()
        cv = open(os.path.join(R, 'work/imgdata', arch, fn), 'rb').read(); im[:330] = gxt.decode(cv, t)[:330]  # 버튼(데이터 이어받기)은 변환본 사용
        x0, y0, x1, y1 = BOX; txt = np.array(textlayer()).astype(np.float32) / 255
        glow = np.array(textlayer().filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32) / 255
        if fn == 'ttl_infoa.img':
            im[y0:y1, x0:x1, 3] = 0
            a = np.clip(np.maximum(txt, glow * 0.85), 0, 1)
            im[..., 3] = np.maximum(im[..., 3], (a * 255).astype(np.uint8))
            im[..., :3] = np.where((a > 0)[..., None], 0, im[..., :3])
        else:
            for y in range(y0, y1):  # 배경을 좌우 가장자리 색으로 보간
                l = im[y, x0 - 1, :3].astype(np.float32); r = im[y, x1, :3].astype(np.float32)
                for x in range(x0, x1): im[y, x, :3] = (l + (r - l) * (x - x0) / (x1 - x0)).astype(np.uint8)
            sh = glow[..., None] * 0.6; c = im[..., :3].astype(np.float32) * (1 - sh) + 30 * sh
            c = c * (1 - txt[..., None]) + 255 * txt[..., None]
            im[..., :3] = np.clip(c, 0, 255).astype(np.uint8)
        nb = gxt.encode(b, t, im)
        open(os.path.join(R, 'work/imgdata', arch, fn), 'wb').write(nb); print(arch, fn)


