"""모든 번역 대상 일본어 문자열을 고유 목록으로 추출하고 배치 파일로 분할"""
import msg,mbe,mvgl,glob,re,os,json,sys
sys.stdout.reconfigure(encoding='utf-8')
jp=re.compile(r'[\u3040-\u30ff\u4e00-\u9fff\uff01-\uff60\u3000-\u303f]')
W='../work/'; order=[]; seen={}; where={}
def add(s,src):
    if not s or not jp.search(s): return
    if s not in seen: seen[s]=len(order); order.append(s); where[s]=src
# 1) message (CRDB + CRDBboot): 시스템 파일 먼저, 시나리오는 이름순
files=sorted(glob.glob(W+'crdb/message/*.dat'))
sysf=[f for f in files if not re.match(r'[a-z]\d{3}_',os.path.basename(f))]
scen=[f for f in files if f not in sysf]
boot=mvgl.MDB(W+'base/CRDBboot.psp2.mvgl')
bootmsgs=[(n,boot.get(d)) for k,n,d in boot.files() if n.endswith('.dat')]
skip={'ngword.bson','staff.dat','staff2.dat','copyright.dat','test.dat'}
for n,b in bootmsgs:
    for a,bb in msg.parse(b)[0]: add(a,'boot/'+n); add(bb,'boot/'+n)
for f in sysf+scen:
    bn=os.path.basename(f)
    for a,b in msg.parse(open(f,'rb').read())[0]:
        add(a,bn)
        if b!='dummy' and not b.startswith('\\d'): add(b,bn)
for f in sorted(glob.glob(W+'crdb/data/*.mbe')):
    h,ch=mbe.parse(open(f,'rb').read())
    for o,r in ch: add(mbe.text(r),os.path.basename(f))
for f in sorted(glob.glob(W+'crdb/data/*.bson')):
    if os.path.basename(f) in skip: continue
    for s in open(f,'rb').read().split(b'\0'):
        try: add(s.decode('utf-8'),os.path.basename(f))
        except UnicodeDecodeError: pass
for f in sorted(glob.glob(W+'crdb/script/*.nut')):
    for s in open(f,'rb').read().split(b'\0'):
        try: t=s.decode('utf-8')
        except UnicodeDecodeError: continue
        if jp.search(t): add(t.rstrip('\x10'),os.path.basename(f))
bad=[s for s in order if '\t' in s or '\n' in s or '\r' in s]
print('unique',len(order),'chars',sum(map(len,order)),'with real newline/tab',len(bad))
os.makedirs(W+'tr/src',exist_ok=True)
json.dump({'order':order,'where':where},open(W+'tr/index.json','w',encoding='utf-8'),ensure_ascii=False)
# batches by ~LIMIT chars, keep same source file together
LIMIT=int(sys.argv[1]) if len(sys.argv)>1 else 14000
bi=0; cur=[]; cl=0
def esc(s): return s.replace('\r','\\r').replace('\n','\\N').replace('\t','\\T')
def flush():
    global bi,cur,cl
    if not cur: return
    with open(W+'tr/src/b%03d.txt'%bi,'w',encoding='utf-8') as f:
        last=None
        for i in cur:
            s=order[i]
            if where[s]!=last: f.write('# '+where[s]+'\n'); last=where[s]
            f.write('%d\t%s\n'%(i,esc(s)))
    bi+=1; cur=[]; cl=0
lastsrc=None
for i,s in enumerate(order):
    if (cl>LIMIT and where[s]!=lastsrc) or cl>LIMIT*1.4: flush()
    cur.append(i); cl+=len(s); lastsrc=where[s]
flush()
print('batches',bi)
