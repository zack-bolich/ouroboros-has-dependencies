const fs=require('fs'),vm=require('vm');
const root=__dirname+'/';
const elements={stack:{value:''},prog:{value:fs.readFileSync(root+'tiny.ul','utf8')},op:{value:''}};
const context={document:{getElementById:id=>elements[id]},alert:message=>{throw Error(message)}};
vm.createContext(context);
const html=fs.readFileSync(root+'../upstream-underload.html','utf8');
vm.runInContext(html.match(/<SCRIPT>([\s\S]*?)<\/SCRIPT>/i)[1],context);
let steps=0;
while(elements.prog.value.length){context.step(0);if(++steps>100000)throw Error('step limit');}
if(elements.op.value!==fs.readFileSync(root+'tiny.smbf','utf8'))throw Error('Underload mismatch');
console.log('Published Underload interpreter: complete fixture PASS');
vm.runInThisContext(fs.readFileSync(root+'../upstream-smbf.js','utf8'));
if(smbf(elements.op.value,'')!==fs.readFileSync(root+'tiny.smatiny','utf8'))throw Error('SMBF mismatch');
console.log('Published SMBF interpreter: complete fixture PASS');
