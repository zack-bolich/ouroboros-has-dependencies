"""Independent small-program checks before running the large relay."""
from pathlib import Path
import subprocess,re,hashlib
R=Path(__file__).resolve().parent

def run(args,output):
    with (R/output).open('wb') as f:subprocess.run(args,stdout=f,check=True,cwd=R)

def reference_smatiny(source):
    # Direct dictionary implementation of the language's moving-PC rule.
    p={}
    for line in source.splitlines():
        m=re.fullmatch(r"(\d+)\. Swap (\d+) with (\d+)\.",line)
        if m:
            k,a,b=map(int,m.groups());p[k]=('swap',a,b)
        else:
            m=re.fullmatch(r"(\d+)\. Output this block's position\.",line)
            assert m,line;p[int(m[1])]=('out',)
    pc=1;out=[];highest=max(p)
    for _ in range(1000000):
        if pc>highest:return ''.join(out).encode('ascii')
        op=p.get(pc,('nop',))
        if op[0]=='out':out.append(chr(pc));pc+=1
        elif op[0]=='swap':
            a,b=op[1:];p[a],p[b]=p.get(b,('nop',)),p.get(a,('nop',))
            highest=max(highest,a,b)
            pc=(b if pc==a else a if pc==b else pc)+1
        else:pc+=1
    raise RuntimeError('reference SMATINY step limit')

for name,text in [('tiny','>'),('sample','><"a'),('syntax','9()+-*/')]:
    run(['perl','../muriel.pl',name+'.mur'],name+'-perl.ul')
    run(['./runtime','muriel',name+'.mur'],name+'.ul')
    assert (R/(name+'-perl.ul')).read_bytes()==(R/(name+'.ul')).read_bytes()
    run(['./runtime','underload',name+'.ul'],name+'.smbf')
    run(['./runtime','smbf',name+'.smbf'],name+'.smatiny')
    run(['./runtime','smatiny',name+'.smatiny'],name+'.ppm')
    assert reference_smatiny((R/(name+'.smatiny')).read_text())==(R/(name+'.ppm')).read_bytes()
    run(['../npiet-1.3f/npiet','-q',name+'.ppm'],name+'.result')
    assert (R/(name+'.result')).read_bytes()==text.encode()
    print(name+': published Muriel, independent SMATINY, published Piet PASS',flush=True)
