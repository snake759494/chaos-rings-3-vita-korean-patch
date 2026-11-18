"""TBGB_0KP.TTC 의 두 폰트에 나눔스퀘어네오 Bold 한글을 병합"""
import sys,os
from fontTools.ttLib import TTFont,TTCollection
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
D=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(D,'..')
SRC=os.path.join(ROOT,'work/base/TBGB_0KP.TTC')
KO=os.path.join(ROOT,'NanumSquareNeo-cBd.ttf')
S=0.95; DY=85
def build(chars,out):
    ko=TTFont(KO); kcm=ko.getBestCmap(); kgs=ko.getGlyphSet()
    col=TTCollection(SRC)
    for fi,f in enumerate(col.fonts):
        cm=f.getBestCmap(); order=list(f.getGlyphOrder()); glyf=f['glyf']; hmtx=f['hmtx']
        vm=f['vmtx'] if 'vmtx' in f else None
        add=[c for c in sorted(chars) if c not in cm and c in kcm]
        for c in add:
            name='ko%04X'%c
            adv=1000 if fi==0 else 960
            w=ko['hmtx'][kcm[c]][0]*S
            dx=(960-w)/2
            pen=TTGlyphPen(None)
            kgs[kcm[c]].draw(TransformPen(pen,(S,0,0,S,dx,DY)))
            g=pen.glyph(); order.append(name); glyf.glyphs[name]=g
            if not hasattr(glyf,'glyphOrder'): pass
            g.recalcBounds(glyf)
            hmtx.metrics[name]=(adv,g.xMin if g.numberOfContours else 0)
            if vm: vm.metrics[name]=(1000,880-(g.yMax if g.numberOfContours else 0))
            for t in f['cmap'].tables:
                if t.isUnicode() and (t.format in (4,12) ) and (c<=0xFFFF or t.format==12):
                    t.cmap[c]=name
        f.setGlyphOrder(order); glyf.glyphOrder=order
        f['maxp'].numGlyphs=len(order)
        if 'LTSH' in f: del f['LTSH']
        if 'hdmx' in f: del f['hdmx']
        print('font',fi,'added',len(add),'glyphs',len(order))
    col.save(out)
if __name__=='__main__':
    chars=set()
    for p in sys.argv[2:]:
        chars|=set(ord(ch) for ch in open(p,encoding='utf-8').read())
    build(chars,sys.argv[1])
