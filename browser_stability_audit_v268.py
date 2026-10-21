import pathlib,subprocess,tempfile,time,json,re,html as htmlmod,threading,http.server,socketserver,shutil,os
ROOT=pathlib.Path(__file__).resolve().parent
PUBLIC=ROOT/"public"; INDEX=PUBLIC/"index.html"
if not INDEX.exists(): raise SystemExit("public/index.html missing")
chrome=next((shutil.which(x) for x in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(x)),None)
if not chrome: raise SystemExit("Chromium/Chrome not found")

audit_js=r"""
<script>
(async function(){
 const out={errors:[],runs:[],musicButtons:[],duplicates:{}};
 addEventListener('error',e=>out.errors.push(String(e.message||e.error||'error')));
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const rect=e=>{const r=e?.getBoundingClientRect?.();return r?[r.left,r.top,r.width,r.height]:null};
 const diff=(a,b)=>!a||!b?0:Math.max(...a.map((x,i)=>Math.abs(x-b[i])));
 function snap(){
   return {
     scrollY:window.scrollY,
     scrollW:document.documentElement.scrollWidth,
     width:document.documentElement.clientWidth,
     hero:rect(document.querySelector('.hero')),
     workspace:rect(document.querySelector('#v266CoachWorkspace')),
     cockpit:rect(document.querySelector('#v268CoachCockpit')),
     profile:rect(document.querySelector('#v114ProfileCard'))
   };
 }
 function dup(id){return document.querySelectorAll('#'+id).length}
 try{
   cloudEnabled=false;supabaseClient=null;
   currentUser={id:'qa-user',email:'qa@local.invalid'};
   currentProfile={id:'qa-user',full_name:'QA Coach',role:'coach'};
   const s=state?.students?.[0]; if(s)state.selectedStudentId=s.id;
   mode='coach';coachTab='student';coachStudentTab='summary';render();
   await sleep(250);
   const base=snap();
   for(let i=0;i<8;i++){
     render();await sleep(90);
     const now=snap();
     out.runs.push({i,overflow:Math.max(0,now.scrollW-now.width),hero:diff(base.hero,now.hero),workspace:diff(base.workspace,now.workspace),cockpit:diff(base.cockpit,now.cockpit),profile:diff(base.profile,now.profile),scrollY:now.scrollY});
   }
   out.duplicates={
     cockpit:dup('v268CoachCockpit'),workspace:dup('v266CoachWorkspace'),
     profile:dup('v114ProfileCard'),coachAvatar:dup('v175CoachAvatarSlot')
   };
   out.musicButtons=[...document.querySelectorAll('button,.tab')].map(x=>(x.textContent||'').trim()).filter(x=>/^Música$/i.test(x));
   mode='student';studentTab='home';render();await sleep(220);
   out.studentAvatarCount=dup('v268StudentAvatarPanel');
   out.studentOverflow=Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth);
   out.activeAnimations=document.getAnimations().filter(a=>a.playState==='running').length;
 }catch(e){out.errors.push(String(e?.stack||e))}
 const p=document.createElement('pre');p.id='v268BrowserResult';p.textContent=JSON.stringify(out);document.body.appendChild(p);
})();
</script>
"""
src=INDEX.read_text(encoding="utf-8")
qa=src.replace("</body>",audit_js+"\n</body>",1)
path=PUBLIC/"__qa_v268.html";path.write_text(qa,encoding="utf-8")
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a): pass
os.chdir(PUBLIC);srv=socketserver.TCPServer(("127.0.0.1",0),Quiet);port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
fails=[];reports=[]
try:
 for w,h in [(1440,1000),(1024,900),(768,900),(500,850)]:
  prof=tempfile.mkdtemp(prefix="fjz-v268-")
  cp=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--disable-background-networking","--hide-scrollbars",f"--window-size={w},{h}",f"--user-data-dir={prof}","--virtual-time-budget=6500","--dump-dom",f"http://127.0.0.1:{port}/__qa_v268.html"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=35)
  m=re.search(r'<pre id="v268BrowserResult">(.*?)</pre>',cp.stdout,re.S)
  if not m: raise SystemExit("V20.68 browser result missing")
  rep=json.loads(htmlmod.unescape(m.group(1)));rep["viewport"]=[w,h];reports.append(rep)
finally:
 srv.shutdown();srv.server_close()
 try:path.unlink()
 except:pass

for r in reports:
 if r["errors"]:fails.append({"vp":r["viewport"],"type":"js","v":r["errors"]})
 if r["musicButtons"]:fails.append({"vp":r["viewport"],"type":"music_button","v":r["musicButtons"]})
 if any(v>1 for v in r["duplicates"].values()):fails.append({"vp":r["viewport"],"type":"duplicates","v":r["duplicates"]})
 if r.get("studentAvatarCount",0)!=1:fails.append({"vp":r["viewport"],"type":"student_avatar","v":r.get("studentAvatarCount")})
 if r.get("studentOverflow",0)>2:fails.append({"vp":r["viewport"],"type":"student_overflow","v":r["studentOverflow"]})
 if r.get("activeAnimations",0)>3:fails.append({"vp":r["viewport"],"type":"animations","v":r["activeAnimations"]})
 for run in r["runs"]:
  if run["overflow"]>2:fails.append({"vp":r["viewport"],"type":"overflow","v":run})
  if run["scrollY"]!=0:fails.append({"vp":r["viewport"],"type":"scroll_drift","v":run})
  if max(run["hero"],run["workspace"],run["cockpit"],run["profile"])>4:fails.append({"vp":r["viewport"],"type":"warp","v":run})

print("TEAM FJZ V20.68 BROWSER STABILITY AUDIT")
print(json.dumps({"viewports":[r["viewport"] for r in reports],"failures":fails},indent=2,ensure_ascii=False))
if fails: raise SystemExit("V20.68 browser stability failures")
print("TEAM FJZ V20.68 BROWSER STABILITY AUDIT OK")
