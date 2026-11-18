import mvgl,os,sys
src,dst=sys.argv[1],sys.argv[2]
m=mvgl.MDB(src)
for k,n,d in m.files():
    p=os.path.join(dst,n.replace(chr(92),'/')); os.makedirs(os.path.dirname(p),exist_ok=True)
    b=m.get(d); assert len(b)==m.data[d][1],n; open(p,'wb').write(b)
