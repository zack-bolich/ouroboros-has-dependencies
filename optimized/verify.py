"""Check the closing bytes and the independently calculated Piet raster."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent

def befunge(code):
    stack=[];x=0;direction=1;quoted=False;out=bytearray()
    def pop():return stack.pop() if stack else 0
    for _ in range(2000000):
        c=code[x]
        if quoted and c!=34:stack.append(c)
        elif c==34:quoted=not quoted
        elif 48<=c<=57:stack.append(c-48)
        elif c==62:direction=1
        elif c==60:direction=-1
        elif c==58:stack.append(stack[-1] if stack else 0)
        elif c in b'+-*':
            v,u=pop(),pop();stack.append(u+v if c==43 else u-v if c==45 else u*v)
        elif c==33:stack.append(int(not pop()))
        elif c==103:
            y=pop();xx=pop();assert y==0;stack.append(code[xx])
        elif c==44:out.append(pop()%256)
        elif c==106:x=(x+direction*pop())%len(code)
        elif c==64:return bytes(out)
        else:raise ValueError(('unexpected Befunge instruction',x,chr(c)))
        x=(x+direction)%len(code)
    raise RuntimeError('Befunge step limit')

seed=(R/'seven.b98').read_bytes()
assert befunge(seed)==(R/'seven.fish').read_bytes()
assert (R/'seven.mur').read_bytes()==(R/'seven.expected.mur').read_bytes()
assert (R/'seven.result').read_bytes()==seed
light=[(255,192,192),(255,255,192),(192,255,192),(192,255,255),(192,192,255),(255,192,255)]
normal=[(255,0,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255)]
def pixel(rgb):return ''.join(f'{v:03d} ' for v in rgb).encode()
w=sum(seed)+len(seed)+2;trap=light[-len(seed)%6]
expected=hashlib.sha256()
def add(rgb,count):expected.update(pixel(rgb)*count)
expected.update(f'P3\n{w} 3\n255\n'.encode())
add(light[0],1);add((0,0,0),w-4);add(trap,3)
for i,c in enumerate(seed):add(light[-i%6],c-(i==0));add(normal[-i%6],1)
add(trap,3);add((0,0,0),w-3);add(trap,3)
actual=hashlib.sha256((R/'seven.ppm').read_bytes()).hexdigest()
assert actual==expected.hexdigest(), 'Piet raster differs from independent layout calculation'
manifest={}
for name in ['seven.b98','seven.fish','seven.mur','seven.ul','seven.smbf','seven.smatiny','seven.ppm']:
    digest=hashlib.sha256();path=R/name
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):digest.update(block)
    manifest[name]={'bytes':path.stat().st_size,'sha256':digest.hexdigest()}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASS: all seven stages close byte for byte; Piet raster independently verified')
for name,info in manifest.items():print(name,info['bytes'])
