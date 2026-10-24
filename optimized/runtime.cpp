// Independent execution tools for the relay. Sources are interpreted, not rebuilt.
#include <bits/stdc++.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
using namespace std;
using I=long long;
#include "optimized-tail.h"
struct E {char op;string s;I n=0;E *a=nullptr,*b=nullptr,*c=nullptr;};
struct St {char op,v=0;E*e;};
struct Parser {
 string_view s;size_t p=0;vector<unique_ptr<E>> nodes;
 Parser(string_view s):s(s){}
 void ws(){while(p<s.size()&&isspace((unsigned char)s[p]))++p;}
 char peek(){ws();return p<s.size()?s[p]:0;}
 void take(char c){if(peek()!=c)throw runtime_error(string("expected ")+c+" near "+string(s.substr(p,80)));++p;}
 E* make(char o,E*a=nullptr,E*b=nullptr,E*c=nullptr){nodes.emplace_back(new E{o,"",0,a,b,c});return nodes.back().get();}
 E* na(){char c=peek();
  if(c=='('){++p;auto e=ne();take(')');return e;}
  if(c=='-'){++p;return make('~',na());}
  if(c=='#'||c=='&'){++p;return make(c,sa());}
  if(islower(c)){++p;auto e=make('v');e->n=c-'a';return e;}
  if(isdigit(c)){I n=0;while(p<s.size()&&isdigit(s[p]))n=n*10+s[p++]-'0';auto e=make('i');e->n=n;return e;}
  throw runtime_error("numeric expression near "+string(s.substr(p,80)));
 }
 E* nf(){auto e=na();while(peek()=='*'){++p;e=make('*',e,na());}return e;}
 E* nt(){auto e=nf();while(peek()=='+'||peek()=='-'){char c=s[p++];e=make(c,e,nf());}return e;}
 E* ne(){auto e=nt();while(peek()=='='||peek()=='>'||peek()=='<'){char c=s[p++];e=make(c,e,nt());}return e;}
 E* sa(){char c=peek();
  if(c=='"'){++p;string r;while(p<s.size()&&s[p]!='"'){char z=s[p++];if(z=='\\'){if(p>=s.size())throw runtime_error("escape EOF");z=s[p++];if(z=='n')z='\n';}r+=z;}take('"');auto e=make('s');e->s=move(r);return e;}
  if(isupper(c)){++p;auto e=make('V');e->n=c-'A';return e;}
  if(c=='('){++p;auto e=se();take(')');return e;}
  if(c=='$'){++p;return make('$',na());}
  if(c=='|'){++p;return make('|',sa());}
  if(c=='%'){++p;auto a=sa();take(',');auto b=ne();take(',');auto z=ne();return make('%',a,b,z);}
  throw runtime_error("string expression near "+string(s.substr(p,80)));
 }
 E* se(){auto e=sa();while(peek()=='+'){++p;e=make('C',e,sa());}return e;}
 vector<St> program(){vector<St> r;while(peek()){
  char c=peek();++p;if(c=='.'||c=='@')r.push_back({c,0,se()});
  else if(isupper(c)||islower(c)){take(':');r.push_back({':',c,isupper(c)?se():ne()});}
  else throw runtime_error("invalid instruction "+string(1,c));
  if(peek()==';')++p;else if(peek())throw runtime_error("expected semicolon near "+string(s.substr(p,80)));
 }return r;}
};
struct Env {array<I,26> n{};array<string,26>s;};
string es(E*,Env&);
I en(E*e,Env&v){switch(e->op){case'i':return e->n;case'v':return v.n[e->n];case'~':return -en(e->a,v);case'#':{auto s=es(e->a,v);size_t p;I n=stoll(s,&p);if(p!=s.size())throw runtime_error("bad numeric string");return n;}case'&':return es(e->a,v).size();}
 I a=en(e->a,v),b=en(e->b,v);switch(e->op){case'+':return a+b;case'-':return a-b;case'*':return a*b;case'=':return a==b;case'>':return a>b;case'<':return a<b;}throw runtime_error("unknown numeric op");}
void append(E*e,Env&v,string&r){if(e->op=='C'){append(e->a,v,r);append(e->b,v,r);return;}r+=es(e,v);}
string es(E*e,Env&v){switch(e->op){case's':return e->s;case'V':return v.s[e->n];case'C':{string r;append(e,v,r);return r;}case'$':return to_string(en(e->a,v));case'|':{string r;for(char c:es(e->a,v)){if(c=='"'||c=='\\')r+='\\';if(c=='\n')r+="\\n";else r+=c;}return r;}case'%':{auto s=es(e->a,v);I a=en(e->b,v),b=en(e->c,v);if(a<0||b<a||b>(I)s.size())throw runtime_error("substring range "+to_string(a)+","+to_string(b)+" of "+to_string(s.size()));return s.substr(a,b-a);}}
 throw runtime_error("unknown string op");}
bool exec(const vector<St>&p,Env&v,string&next){for(auto st:p){if(st.op==':'){if(isupper(st.v))v.s[st.v-'A']=es(st.e,v);else v.n[st.v-'a']=en(st.e,v);}else if(st.op=='.')cout<<es(st.e,v);else{next=es(st.e,v);return true;}}return false;}
string readfile(const string&p){ifstream f(p,ios::binary);if(!f)throw runtime_error("open "+p);return string(istreambuf_iterator<char>(f),{});}
void muriel(const string&file){string code=readfile(file),cached;unique_ptr<Parser> cacheparser;vector<St> cachebody;Env env;I generations=0;
 while(!code.empty()){
  bool optimized=!cached.empty()&&code.size()>=cached.size()&&code.compare(code.size()-cached.size(),cached.size(),cached)==0;
  string_view prefix(code.data(),code.size()-(optimized?cached.size():0));Parser parser(prefix);auto body=parser.program();string next;
  bool replaced=exec(body,env,next);
  // Compile the generated self-replacement tail into direct state transfer.
  // This only fires for the exact checked serializer in optimized-tail.h.
  // Reset all non-serialized variables, preserving @'s fresh-environment rule.
  if(!replaced&&optimized&&cached.size()>=optimized_tail.size()&&
      cached.compare(cached.size()-optimized_tail.size(),optimized_tail.size(),optimized_tail)==0){
    vector<St> fastbody(cachebody.begin(),cachebody.end()-2);
    map<string,pair<unique_ptr<Parser>,vector<St>>> actions;
    const string ss=saved_strings, nn=saved_numbers;
    while(true){
      string ignored;
      if(exec(fastbody,env,ignored))throw runtime_error("unexpected replacement in compiled body");
      string action=env.n['r'-'a']==0?env.s['G'-'A']:"";
      for(int x=0;x<26;++x){if(ss.find(char('A'+x))==string::npos)env.s[x].clear();if(nn.find(char('a'+x))==string::npos)env.n[x]=0;}
      ++generations;
      if(generations%500000==0)cerr<<"Muriel replacements: "<<generations<<"\n";
      if(!action.empty()){
        auto it=actions.find(action);
        if(it==actions.end()){
          auto parser=make_unique<Parser>(action);auto statements=parser->program();
          it=actions.emplace(action,make_pair(move(parser),move(statements))).first;
        }
        string target;
        if(exec(it->second.second,env,target)){
          if(!target.empty())throw runtime_error("compiled action replacement is nonempty");
          cerr<<"Muriel total replacements: "<<generations+1<<"\n";return;
        }
      }
    }
  }
  if(!replaced&&optimized)replaced=exec(cachebody,env,next);
  if(!replaced)break;
  auto&t=env.s['T'-'A'];if(!t.empty()&&t!=cached){cached=t;cacheparser=make_unique<Parser>(cached);cachebody=cacheparser->program();}
  env=Env{};code=move(next);++generations;
  if(generations%500000==0)cerr<<"Muriel replacements: "<<generations<<"\n";
 }
 cerr<<"Muriel total replacements: "<<generations<<"\n";
}
void underload(const string&file){ifstream f(file,ios::binary);vector<string> stack;string eval;size_t ep=0;I count=0,dups=0;
 auto next=[&]()->int {if(ep<eval.size())return (unsigned char)eval[ep++];return f.get();};
 auto pop=[&](){if(stack.empty())throw runtime_error("Underload underflow");string r=move(stack.back());stack.pop_back();return r;};
 for(int c;(c=next())!=EOF;){++count;switch(c){case'(':{string s;int depth=1;while(depth){int z=next();if(z==EOF)throw runtime_error("Underload unmatched quote");depth+=(z=='(')-(z==')');if(depth)s+=char(z);}stack.push_back(move(s));break;}
 case':':if(stack.empty())throw runtime_error("Underload dup underflow");stack.push_back(stack.back());++dups;break;
 case'*':{auto b=pop();if(stack.empty())throw runtime_error("Underload concat underflow");stack.back()+=b;break;}
 case'S':cout<<pop();break;
 case'^':{auto s=pop();eval=s+eval.substr(ep);ep=0;break;}
 case'~':{auto a=pop(),b=pop();stack.push_back(move(a));stack.push_back(move(b));break;}
 case'a':{auto a=pop();stack.push_back("("+a+")");break;}
 case'!':pop();break;
 default:throw runtime_error("Underload invalid opcode");}}
 if(!stack.empty())throw runtime_error("Underload leftover stack");cerr<<"Underload instructions "<<count<<", duplications "<<dups<<"\n";
}
void smbf(const string&file){int fd=open(file.c_str(),O_RDONLY);if(fd<0)throw runtime_error("SMBF open");I len=lseek(fd,0,SEEK_END);auto mem=(unsigned char*)mmap(nullptr,len,PROT_READ|PROT_WRITE,MAP_PRIVATE,fd,0);if(mem==MAP_FAILED)throw runtime_error("SMBF mmap");I ip=0,dp=len,steps=0,writes=0;unsigned char end=0;
 const I cap=min<I>(4096,len);vector<I> runs(cap),jumps(cap,-1);
 auto invalidate=[&](){fill(runs.begin(),runs.end(),0);fill(jumps.begin(),jumps.end(),-1);};
 auto cell=[&]()->unsigned char& {if(dp==len)return end;if(dp<0||dp>len)throw runtime_error("SMBF tape range");return mem[dp];};
 while(ip<len){char c=mem[ip];switch(c){case'<':--dp;break;case'>':++dp;break;case'+':case'-':{
 I count=ip<cap?runs[ip]:0;
 if(!count){count=1;while(ip+count<len&&mem[ip+count]==c)++count;if(ip+count<=cap)runs[ip]=count;}
 if(dp>=ip&&dp<ip+count)count=1; // Writing a future instruction defeats folding.
 cell()=(unsigned char)(cell()+(c=='+'?count:-count));writes+=count;steps+=count-1;
 if(dp<cap)invalidate();ip+=count-1;break;}
case'.':cout.put(cell());break;
 case'[':if(!cell()){
 I origin=ip;if(ip<cap&&jumps[ip]>=0)ip=jumps[ip];else{
 I d=1;while(d){if(++ip>=len)throw runtime_error("SMBF unmatched [");d+=(mem[ip]=='[')-(mem[ip]==']');}
 if(ip<cap){jumps[origin]=ip;jumps[ip]=origin;}}
 }break;
 case']':if(cell()){
 I origin=ip;if(ip<cap&&jumps[ip]>=0)ip=jumps[ip];else{
 I d=1;while(d){if(--ip<0)throw runtime_error("SMBF unmatched ]");d+=(mem[ip]==']')-(mem[ip]=='[');}
 if(origin<cap){jumps[origin]=ip;jumps[ip]=origin;}}
 }break;
 case',':throw runtime_error("unexpected input");}++ip;if(++steps>1000000000000LL)throw runtime_error("SMBF step limit");}
 cerr<<"SMBF steps "<<steps<<", tape writes "<<writes<<"\n";munmap(mem,len);close(fd);
}
struct Instruction{int a=0,b=0;};
void smatiny(const string&file){ifstream f(file);vector<Instruction>v(501);string line;I count=0;int highest=0;
 while(getline(f,line)){int k,a,b;char tail;
  if(sscanf(line.c_str(),"%d. Swap %d with %d.%c",&k,&a,&b,&tail)==3){if(k<=0||a<=0||b<=0)throw runtime_error("SMATINY invalid position");if(k>=(int)v.size())v.resize(max(k+1,(int)v.size()*2));v[k]={a,b};}
  else if(sscanf(line.c_str(),"%d. %c",&k,&tail)==2&&line.substr(line.find(". ")+2)=="Output this block's position."){if(k>=(int)v.size())v.resize(max(k+1,(int)v.size()*2));v[k]={-1,0};}
  else throw runtime_error("SMATINY parse "+line);
  if(k<=highest)throw runtime_error("SMATINY step ordering");highest=k;
 }
 int ip=1;I swaps=0;while(ip<=highest){auto ins=v[ip];if(ins.a==-1){if(ip<0||ip>127)throw runtime_error("SMATINY non-ASCII output");cout.put((char)ip);++ip;}else if(ins.a){if(max(ins.a,ins.b)>=(int)v.size())v.resize(max(ins.a,ins.b)+1);swap(v[ins.a],v[ins.b]);int prev=ip;if(ip==ins.a)ip=ins.b;else if(ip==ins.b)ip=ins.a;ip++;++swaps;while(highest>0&&v[highest].a==0)--highest;}else ++ip;
  if(++count>10000000000LL)throw runtime_error("SMATINY step limit");}
 cerr<<"SMATINY executed "<<count<<" steps, "<<swaps<<" swaps\n";
}
int main(int argc,char**argv){try{if(argc!=3)throw runtime_error("usage: runtime muriel|underload|smbf|smatiny source");ios::sync_with_stdio(false);if(string(argv[1])=="muriel")muriel(argv[2]);else if(string(argv[1])=="underload")underload(argv[2]);else if(string(argv[1])=="smbf")smbf(argv[2]);else if(string(argv[1])=="smatiny")smatiny(argv[2]);else throw runtime_error("unknown mode");}catch(exception&e){cerr<<e.what()<<"\n";return 1;}}
