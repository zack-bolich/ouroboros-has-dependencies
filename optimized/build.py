"""Seven-language relay. No stage reads files, stdin, or another stage's source.
Piet source is canonical ASCII PPM; all outputs are raw bytes, with no newline added.
"""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parent

def mq(s):
    return '"'+s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'

def ul_print(s):
    # Factor repeated punctuation with Underload's duplication/concatenation.
    import re
    out=[]
    for m in re.finditer(r'(.)\1*',s):
        ch=m[1]; n=len(m[0])
        if n<5: out.append('('+m[0]+')S');continue
        expr='('+ch+')'
        for bit in bin(n)[3:]:
            expr+=':*'
            if bit=='1':expr+='('+ch+')*'
        out.append(expr+'S')
    return ''.join(out)

SCAN='<<<'+'-'*33+'['+'+'*33+'<'+'-'*33+']'+'+'*33+'<'+'+'*33+'>>'+'-'*33+'['+'+'*33+'.>'+'-'*33+']'
MAIN=20000
LEVELS=22
STRIDE=300
SM_HEADER=f'1. Swap 1 with {MAIN-1}.\n'
UL_PREFIX=ul_print(SCAN+':!')+'('+SM_HEADER+')S'
UL_SUFFIX='(!])S'
LIGHT=[(255,192,192),(255,255,192),(192,255,192),(192,255,255),(192,192,255),(255,192,255)]
NORMAL=[(255,0,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255)]
def packed_pixel(rgb):return ''.join(f'{ord(c):03d}' for c in ''.join(f'{x:03d} ' for x in rgb))
Y=''.join(packed_pixel(c) for c in LIGHT)
Z=''.join(packed_pixel(c) for c in NORMAL)
BLACK=packed_pixel((0,0,0))
def pack(s):return ''.join(f'{ord(c):03d}' for c in s)

# Construct one-shot (five-step) or reusable (seven-step) output code.
def sn(name,offset=0):return '$'+('('+name+('+' if offset>=0 else '')+str(offset)+')' if offset else name)
def sm_expr(reusable=False):
    terms=[]
    def lit(s):terms.append(mq(s))
    def num(n,o=0):terms.append(sn(n,o))
    num('k');lit('. Swap ');num('k',3);lit(' with ');num('c');lit('.\n')
    num('k',1);lit('. Swap ');num('k',4);lit(' with ');num('c',1);lit('.\n')
    num('k',2);lit('. Swap ');num('k',2);lit(' with ');num('c',-1);lit('.\n')
    num('k',3);lit(". Output this block's position.\n")
    num('k',4);lit('. Swap ');num('c',1);lit(' with ');num('k',4);lit('.\n')
    if reusable:
        num('k',5);lit('. Swap ');num('k',3);lit(' with ');num('c');lit('.\n')
        num('k',6);lit('. Swap ');num('k',2);lit(' with ');num('c',-1);lit('.\n')
    return '+'.join(terms)

def call_expr(offset=0):
    # a = callee entry, e = callee return slot. Restore the jumping instruction.
    terms=[]
    def lit(x):terms.append(mq(x))
    def num(x,o=0):terms.append(sn(x,o))
    num('k',offset);lit('. Swap ');num('k',offset+2);lit(' with ');num('e');lit('.\n')
    num('k',offset+1);lit('. Swap ');num('k',offset+1);lit(' with ');num('a',-1);lit('.\n')
    num('k',offset+2);lit('. Swap ');num('e');lit(' with ');num('k',offset+2);lit('.\n')
    num('k',offset+3);lit('. Swap ');num('k',offset+1);lit(' with ');num('a',-1);lit('.\n')
    return '+'.join(terms)

ACTIONS=[
 'J:"0"+$(48+#(%B,j,j+1));j:j+1;r:1;p:(j=&B);',
 'J:'+mq(pack(' 3\n255\n'))+';r:1;p:2;',
 'J:(%Y,0,36);v:0;r:1;p:3;',
 'J:'+mq(BLACK)+';v:12;r:w-4;p:4;',
 'J:(%Y,q*36,(q+1)*36);v:q;r:3;p:5;',
 'i:0;h:0;v:0;J:(%Y,0,36);r:(#(%X,1,4))-1;p:6;',
 'J:(%Z,h*36,(h+1)*36);v:6+h;r:1;p:7;',
 'i:i+1;h:(h-1)+(6*(h=0));v:h;J:(%Y,h*36,(h+1)*36);'
 'C:X+"1000";r:((#(%C,(i*4)+1,(i*4)+4))*(n>i))+(3*(i=n));p:6+(2*(i=n));',
 'J:'+mq(BLACK)+';v:12;r:w-3;p:9;',
 'J:(%Y,q*36,(q+1)*36);v:q;r:3;p:10;',
 '.'+mq(UL_SUFFIX)+';@(%"x",0,0);',
]
STRINGS=['X','Y','Z','T','J','B','F']
NUMBERS=['w','n','q','p','j','i','h','r','t','k','b','v']
def serialization(strings=STRINGS,numbers=NUMBERS):
    terms=[]
    for v in strings:terms += [mq(v+':"'),'|'+v,mq('";')]
    for v in numbers:terms += [mq(v+':'),'$'+v,mq(';')]
    return '+'.join(terms)
SER=serialization()
POWERS=''.join(f'{2**b:07d}' for b in range(LEVELS))
# Main emits an ordinary one-shot header, then calls shared reversible routines
# for whole runs of identical pixels. Dj emits 2**j copies of its colour token.
T=('c:#(%J,t,t+3);d:#(%F,b*7,(b+1)*7);g:(r>d)+(r=d);'
   'a:1000+(v*300)+(b=0)+(87+((b-1)*10))*(b>0);'
   'e:((1000+(v*300)+85)*(b=0))+((a+8)*(b>0));'
   'O:'+mq('(')+'+'+sm_expr()+'+'+mq(')S')+';'
   'P:'+mq('(')+'+'+call_expr()+'+'+mq(')S')+';'
   '.(%O,0,&O*(3>p))+(%P,0,&P*(p>2)*g);'
   'k:k+(5*(3>p))+(4*(p>2)*g);'
   't:t+(3*(3>p));r:r-((t=&J)*(3>p));t:t*(&J>t);'
   'r:r-(d*g*(p>2));b:b-(p>2);b:(b*(r>0))+('+str(LEVELS-1)+'*(r=0));')
for i,action in enumerate(ACTIONS):
    T+='A:'+mq(action)+';G:'+('G+' if i else '')+'(%A,0,&A*(p='+str(i)+'));'
T+='N:'+SER+'+(%G,0,&G*(r=0))+T;@N'

INIT=('p:0;j:0;i:0;h:0;r:1;t:0;k:'+str(MAIN)+';b:'+str(LEVELS-1)+';v:0;'
      'J:'+mq(pack('P3\n'))+';')
LIB_STRINGS=['X','Y','Z','T','L','J','B','F']
LIB_NUMBERS=['w','n','q','l','j','f']
LIB_SER=serialization(LIB_STRINGS,LIB_NUMBERS)
L=('d:1000+(l*300);'
   'C:Y+Z+'+mq(BLACK)+';'
   'c:#(%C,(l*36)+(j*3*(f=0)),(l*36)+(j*3*(f=0))+3);'
   'k:((d+1+(j*7))*(f=0))+((d+87+((j-1)*10))*(f=1));'
   'a:((d+1)*(j=1))+((d+87+((j-2)*10))*(j>1));'
   'e:((d+85)*(j=1))+((a+8)*(j>1));'
   'O:'+sm_expr(True)+';P:'+call_expr()+'+'+call_expr(4)+';'
   '.'+mq('(')+'+(%O,0,&O*(f=0))+(%P,0,&P*(f=1))+'+mq(')S')+';'
   'j:j+1;g:(f=0)*(j=12);d:(f=1)*(j='+str(LEVELS)+');'
   'l:l+d;f:(f+g)*(1-d);j:((j*(1-g))+g)*(1-d);'
   'G:'+mq(INIT)+'+T;N:'+LIB_SER+'+(%L,0,&L*(13>l))+(%G,0,&G*(l=13));@N')

def muriel_parts(n):
    prefix=('Y:'+mq(Y)+';Z:'+mq(Z)+';T:'+mq(T)+';L:'+mq(L)+';F:'+mq(POWERS)+';'
            'n:'+f'{n:05d}'+';q:'+str((-n)%6)+';X:"1062')
    tail=';B:$w;l:0;j:0;f:0;J:'+mq(pack('P3\n'))+';.'+mq(UL_PREFIX)+';N:'+LIB_SER+'+L;@N'
    return prefix,tail

WIDTH=5

def bn(n):
    s=f'{abs(n):0{WIDTH}d}';res=s[0]+''.join('91+*'+d+'+' for d in s[1:])
    return '0'+res+'-' if n<0 else res

def fn(n):
    assert 0<=n<10**WIDTH,n
    s=f'{n:0{WIDTH}d}';return s[0]+''.join('a*'+d+'+' for d in s[1:])

# Fish assembler: code executes leftwards. A portal jumps to the cell before
# the desired instruction, matching the published Fish interpreter.
class Fish:
    def __init__(self):self.parts=[];self.labels={}
    def add(self,s):self.parts.append(s)
    def label(self,n):self.labels[n]=sum(map(len,self.parts))
    def jump(self,label):self.add(('@'+label+'@').ljust(len(fn(0)),'_')+'0.')
    def branch(self,yes,no):
        # flag on stack; choose between forward addresses arithmetically.
        self.add(('!'+yes+'!'+no+'!').ljust(2*len(fn(0))+len('*+0.'),'_'))
    def finish(self,n):
        import re
        s=''.join(self.parts)
        for name,off in self.labels.items():
            marker=('@'+name+'@').ljust(len(fn(0)),'_');s=s.replace(marker,fn(n-off))
        pattern=r'!([^!]+)!([^!]+)!_+'
        def br(m):
            y,z=(n-self.labels[x] for x in m.groups())
            if y<z:raise ValueError(('branch order',y,z))
            return fn(y-z)+'*'+fn(z)+'+0.'
        return re.sub(pattern,br,s)


def make(n,jump):
    bp='"<",1'; b=bp+':0g,1+:'+bn(n)+'-!!'+bn(jump)+'*j@'
    prefix,tail=muriel_parts(n)
    data_start=1+len(b); prefix_end=data_start+len(prefix); tail_end=prefix_end+len(tail)
    f=Fish()
    def print_range(start,end,label,next_label):
        f.add(fn(start));f.label(label);f.add(':0g:0='+fn(32)+'*+o1+:'+fn(end)+'=0=');f.branch(label,next_label);f.label(next_label);f.add('~')
    print_range(data_start,prefix_end,'prefix','sourceinit')
    f.add(fn(65)+'1');f.label('source')
    f.add(':0g:0='+fn(32)+'*+:'+fn(1000)+'+n$&1++&1+:'+fn(n)+'=0=');f.branch('source','sourceend');f.label('sourceend')
    f.add('~')
    # Emit quote, semicolon, w colon without quoting Fish syntax.
    for c in '";w:':f.add(fn(ord(c))+'o')
    f.add('n')
    print_range(prefix_end,tail_end,'tail','halt');f.add(';')
    text=f.finish(n)
    assert len(text)==sum(map(len,f.parts))
    return '>'+b+prefix+tail+text[::-1],len(bp)+1,1+len(b)-2

n=5000
for _ in range(20):
    a,loop,j=make(n,-64)
    n=len(a)
    a,loop,j=make(n,loop-j-1)
    if len(a)==n:break
assert len(a)==n and n<99999
assert sum(a.encode())+len(a)+2<2**LEVELS
# Rebuild once all embedded lengths and jump addresses are stable.
a,loop,j=make(n,loop-j-1)
b='<'+a[1:]
(ROOT/'seven.b98').write_text(a)
(ROOT/'seven.fish').write_text(b)
prefix,tail=muriel_parts(n)
expected=prefix+''.join(str(1000+ord(ch)) for ch in a[1:])+'\";w:'+str(sum(a.encode())+len(a)+2)+tail
(ROOT/'seven.expected.mur').write_text(expected)
(ROOT/'template.mur').write_text(T)
(ROOT/'optimized-tail.h').write_text('static const std::string optimized_tail=R"MURIEL('+T[T.rindex('N:'):]+')MURIEL";\nstatic const std::string saved_strings="'+''.join(STRINGS)+'";\nstatic const std::string saved_numbers="'+''.join(NUMBERS)+'";\n')
(ROOT/'expected-width.txt').write_text(str(sum(a.encode())+len(a)+2))
print('Source stages:',len(a),'bytes; Piet width:',sum(a.encode())+len(a)+2)

# Minimal complete Muriel fixtures exercise every Piet layout phase.
for name,data in [('tiny','>'),('sample','><"a'),('syntax','9()+-*/')]:
    prefix,tail=muriel_parts(len(data));prefix=prefix[:-4]+''.join(str(1000+ord(c)) for c in data)
    source=prefix+'";w:'+str(sum(data.encode())+len(data)+2)+tail
    (ROOT/(name+'.mur')).write_text(source)
