"""번역 배치 검증: python check_tr.py [bNNN ...]  (인자 없으면 전체)"""
import re,sys,glob,os
sys.stdout.reconfigure(encoding='utf-8')
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','work','tr')
CODE=re.compile(r'\\[dw][0-9]+|\\[a-zA-Z*@]|\{[^}]*\}|%[0-9]*[sd]')
KANA=re.compile(r'[\u3041-\u30fa]')
def load(p):
    d={}
    if not os.path.exists(p): return None
    for ln in open(p,encoding='utf-8'):
        ln=ln.rstrip('\n')
        if not ln or ln.startswith('#'): continue
        if '\t' not in ln: continue
        i,s=ln.split('\t',1)
        if i.strip().isdigit(): d[int(i)]=s
    return d
def wid(s):
    s=CODE.sub('',s)
    return sum(0.5 if ord(c)<0x2000 or c in ' ' else 1 for c in s)
def norm_codes(s):
    return sorted(c for c in CODE.findall(s) if c not in ('\\n',))
def check(b,verbose=True):
    src=load(f'{W}/src/{b}.txt'); out=load(f'{W}/out/{b}.txt')
    if out is None: return None
    miss=[i for i in src if i not in out]; probs=[]
    for i,ja in src.items():
        if i not in out: continue
        ko=out[i]
        if norm_codes(ja)!=norm_codes(ko): probs.append((i,'코드불일치',ja,ko))
        elif ja.count('\\n')!=ko.count('\\n') and ja.count('\\n')>0: probs.append((i,'줄수다름',ja,ko))
        if KANA.search(ko): probs.append((i,'가나잔존',ja,ko))
        for lj,lk in zip(ja.split('\\n'),ko.split('\\n')):
            if wid(lk)>wid(lj)+2 and wid(lk)>22: probs.append((i,'줄길이초과(%.1f>%.1f)'%(wid(lk),wid(lj)),ja,ko)); break
    if verbose:
        print(b,'src',len(src),'out',len(out),'missing',len(miss),'problems',len(probs))
        for p in probs[:30]: print('  ',p)
        if miss: print('   missing ids:',miss[:20])
    return len(miss),probs
if __name__=='__main__':
    bs=sys.argv[1:] or sorted(os.path.basename(f)[:-4] for f in glob.glob(W+'/src/b*.txt'))
    for b in bs: check(b)
