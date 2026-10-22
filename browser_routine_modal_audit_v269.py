import pathlib,subprocess,tempfile,json,re,html as htmlmod,threading,http.server,socketserver,shutil,os
ROOT=pathlib.Path(__file__).resolve().parent
PUBLIC=ROOT/"public"; INDEX=PUBLIC/"index.html"
chrome=next((shutil.which(x) for x in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(x)),None)
if not chrome: raise SystemExit("Chrome/Chromium not found")

audit_js=r"""
<script>
(async function(){
 const out={errors:[],checks:[]};
 addEventListener('error',e=>out.errors.push(String(e.message||e.error||'error')));
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const visible=e=>{if(!e)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
 function measure(name){
   const modal=el('modal'),r=modal?.getBoundingClientRect?.(),vw=document.documentElement.clientWidth;
   const bad=[...document.querySelectorAll('#modal input,#modal select,#modal button,#modal h3,#modal .library-item')].filter(visible).filter(e=>{const x=e.getBoundingClientRect();return x.left<(r?.left||0)-2||x.right>(r?.right||vw)+2||x.width>(r?.width||vw)+2}).map(e=>({tag:e.tagName,cls:e.className,text:(e.textContent||'').trim().slice(0,60)}));
   out.checks.push({name,docOverflow:Math.max(0,document.documentElement.scrollWidth-vw),modal:r?[r.left,r.top,r.width,r.height]:null,bad});
 }
 try{
   cloudEnabled=false;supabaseClient=null;
   currentProfile={id:'qa',role:'coach',full_name:'QA Coach'};currentUser={id:'qa'};
   mode='coach';coachTab='student';coachStudentTab='routine';
   if(state?.students?.[0])state.selectedStudentId=state.students[0].id;
   render();await sleep(120);

   openLibrary(0);await sleep(80);
   measure('library');
   out.mainHasPreparation=[...document.querySelectorAll('#muscleFilter option')].some(o=>/Calentamiento|Estiramientos/i.test(o.textContent||''));
   customExercise(0);await sleep(80);
   measure('add-exercise');
   out.backButton=!!document.querySelector('.v269-back-btn');
   openPrepLibraryV269(0,'warmup');await sleep(80);
   measure('warmup-library');
   out.warmupHasItems=document.querySelectorAll('#v269PrepGrid .library-item').length>0;
   closeModal();
   render();await sleep(120);
   out.prepEditor=!!document.querySelector('.v269-prep-editor');
 }catch(e){out.errors.push(String(e?.stack||e))}
 const p=document.createElement('pre');p.id='v269AuditResult';p.textContent=JSON.stringify(out);document.body.appendChild(p);
})();
</script>
"""
src=INDEX.read_text(encoding="utf-8");qa=src.replace("</body>",audit_js+"\n</body>",1)
path=PUBLIC/"__qa_v269.html";path.write_text(qa,encoding="utf-8")
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a): pass
os.chdir(PUBLIC);srv=socketserver.TCPServer(("127.0.0.1",0),Quiet);port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
fails=[];reports=[]
try:
 for w,h in [(1440,1000),(768,900),(500,850)]:
  prof=tempfile.mkdtemp(prefix="fjz-v269-")
  cp=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--disable-background-networking","--hide-scrollbars",f"--window-size={w},{h}",f"--user-data-dir={prof}","--virtual-time-budget=5500","--dump-dom",f"http://127.0.0.1:{port}/__qa_v269.html"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=35)
  m=re.search(r'<pre id="v269AuditResult">(.*?)</pre>',cp.stdout,re.S)
  if not m: raise SystemExit("V20.69 browser result missing")
  rep=json.loads(htmlmod.unescape(m.group(1)));rep["viewport"]=[w,h];reports.append(rep)
finally:
 srv.shutdown();srv.server_close()
 try:path.unlink()
 except:pass
for r in reports:
 if r["errors"]:fails.append({"vp":r["viewport"],"type":"js","v":r["errors"]})
 if r.get("mainHasPreparation"):fails.append({"vp":r["viewport"],"type":"prep_in_main_library"})
 if not r.get("backButton"):fails.append({"vp":r["viewport"],"type":"missing_back_button"})
 if not r.get("warmupHasItems"):fails.append({"vp":r["viewport"],"type":"empty_warmup_library"})
 if not r.get("prepEditor"):fails.append({"vp":r["viewport"],"type":"missing_prep_editor"})
 for c in r.get("checks",[]):
  if c.get("docOverflow",0)>2:fails.append({"vp":r["viewport"],"type":"doc_overflow","v":c})
  if c.get("bad"):fails.append({"vp":r["viewport"],"type":"modal_overflow","v":c})
print("TEAM FJZ V20.69 ROUTINE MODAL BROWSER AUDIT")
print(json.dumps({"reports":reports,"failures":fails},indent=2,ensure_ascii=False))
if fails: raise SystemExit("V20.69 routine modal/browser failures")
print("TEAM FJZ V20.69 ROUTINE MODAL BROWSER AUDIT OK")
