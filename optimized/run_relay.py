"""Rebuild and execute the seven-stage relay using local interpreters."""
from pathlib import Path
import subprocess,sys,argparse
R=Path(__file__).resolve().parent

def call(args,output=None,cwd=R):
    print('Running:', ' '.join(map(str,args)),flush=True)
    if output:
        with (R/output).open('wb') as f:subprocess.run(args,cwd=cwd,stdout=f,check=True)
    else:subprocess.run(args,cwd=cwd,check=True)

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--fixtures',action='store_true',help='also compare complete small fixtures with published/reference interpreters')
a=p.parse_args()
call([sys.executable,'build.py'])
call(['g++','-O3','-std=c++17','runtime.cpp','-o','runtime'])
npiet=R.parent/'npiet-1.3f'/'npiet'
if not npiet.exists():
    call(['sh','./configure'],cwd=npiet.parent)
    call(['make','npiet'],cwd=npiet.parent)
if a.fixtures:
    call([sys.executable,'check_fixtures.py'])
    call(['node','check_published.js'])
call([sys.executable,'run_fish.py'])
call(['./runtime','muriel','seven.mur'],'seven.ul')
call(['./runtime','underload','seven.ul'],'seven.smbf')
call(['./runtime','smbf','seven.smbf'],'seven.smatiny')
call(['./runtime','smatiny','seven.smatiny'],'seven.ppm')
call([str(npiet),'-q','seven.ppm'],'seven.result')
call([sys.executable,'verify.py'])
