import pathlib,subprocess,tempfile,time,json,re,html as htmlmod,threading,http.server,socketserver,shutil,sys,os

ROOT=pathlib.Path(__file__).resolve().parent
PUBLIC=ROOT/"public"
INDEX=PUBLIC/"index.html"
if not INDEX.exists():
    raise SystemExit("public/index.html missing")

chrome=next((shutil.which(x) for x in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(x)),None)
if not chrome:
    raise SystemExit("Chromium/Chrome not found on QA runner")

audit_js=r"""
<script>
(async function(){
  const result={version:'20.65',viewport:{w:innerWidth,h:innerHeight},views:[],errors:[],health:{}};
  window.addEventListener('error',e=>result.errors.push(String(e.message||e.error||'window error')));

  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const structural=[
    '.card','.hero','.student-row','.day-card','.exercise-row','.workout-card','.session-card',
    '.track-row','.history-item','.modal','.v252-column','.v253-flow-item','.v254-exercise-card',
    '.v259-calendar-card','.v259-month','.v259-upcoming','.v260-four-week','.v258-current-plan',
    '.v249-progress-pulse','.v250-weekly-brief'
  ].join(',');

  function visible(el){
    const cs=getComputedStyle(el),r=el.getBoundingClientRect();
    return cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)!==0&&r.width>0&&r.height>0;
  }
  function allowedOverflow(el){
    const cs=getComputedStyle(el);
    return ['auto','scroll'].includes(cs.overflowX)||
      !!el.closest('.table-wrap,.chart-wrap,.tabs,[class*="table-scroll"]')||
      el.id==='fjzStagingLocalBanner';
  }
  function keyFor(el,i){
    if(el.id)return '#'+el.id;
    const cls=[...el.classList].slice(0,3).join('.');
    return el.tagName.toLowerCase()+(cls?'.'+cls:'')+'@'+i;
  }
  function snapshot(){
    const out={};
    [...document.querySelectorAll(structural)].filter(visible).forEach((el,i)=>{
      const r=el.getBoundingClientRect();
      out[keyFor(el,i)]=[r.left,r.top,r.width,r.height];
    });
    return out;
  }
  function scan(name,renderMs,warpA,warpB){
    const viewportW=document.documentElement.clientWidth||innerWidth;
    const docOverflow=Math.max(0,document.documentElement.scrollWidth-viewportW);
    const overflow=[];
    const controls=[];
    const geometryTransitions=[];
    const nodes=[...document.querySelectorAll(structural)].filter(visible);

    nodes.forEach((el,i)=>{
      const r=el.getBoundingClientRect(),cs=getComputedStyle(el);
      if(!allowedOverflow(el)&&(r.left < -2 || r.right > viewportW+2 || r.width > viewportW+2)){
        overflow.push({el:keyFor(el,i),left:+r.left.toFixed(1),right:+r.right.toFixed(1),width:+r.width.toFixed(1)});
      }
      const tp=String(cs.transitionProperty||'');
      if(/\b(all|width|height|margin|padding|left|right|top|bottom|transform)\b/i.test(tp)){
        geometryTransitions.push({el:keyFor(el,i),transition:tp});
      }
    });

    [...document.querySelectorAll('input,select,textarea,button')].filter(visible).forEach((el,i)=>{
      const parent=el.closest('.card,.hero,.modal,.student-row,.day-card,.exercise-row,.workout-card,.session-card,.track-row,.history-item');
      if(!parent)return;
      const r=el.getBoundingClientRect(),p=parent.getBoundingClientRect();
      if(r.left < p.left-3 || r.right > p.right+3 || r.width > p.width+3){
        controls.push({el:keyFor(el,i),parent:keyFor(parent,i),left:+r.left.toFixed(1),right:+r.right.toFixed(1),parentRight:+p.right.toFixed(1)});
      }
    });

    const shifts=[];
    if(warpA&&warpB){
      Object.keys(warpA).forEach(k=>{
        if(!warpB[k])return;
        const a=warpA[k],b=warpB[k];
        const delta=Math.max(...a.map((v,j)=>Math.abs(v-b[j])));
        if(delta>3)shifts.push({el:k,delta:+delta.toFixed(1),from:a.map(x=>+x.toFixed(1)),to:b.map(x=>+x.toFixed(1))});
      });
    }

    result.views.push({
      name,renderMs:+renderMs.toFixed(1),docOverflow,
      structuralCount:nodes.length,
      overflow:overflow.slice(0,30),
      controls:controls.slice(0,30),
      geometryTransitions:geometryTransitions.slice(0,30),
      shifts:shifts.slice(0,30),
      activeAnimations:document.getAnimations().filter(a=>a.playState==='running').length
    });
  }

  async function visit(name,setup){
    try{
      setup();
      const t0=performance.now();
      render();
      const renderMs=performance.now()-t0;
      await sleep(300);
      const a=snapshot();
      await sleep(180);
      const b=snapshot();
      scan(name,renderMs,a,b);
    }catch(e){
      result.errors.push(name+': '+String(e?.stack||e));
    }
  }

  try{
    cloudEnabled=false;supabaseClient=null;
    currentUser={id:'qa-user',email:'qa@local.invalid'};
    currentProfile={id:'qa-user',full_name:'QA Coach',role:'coach'};
    const first=state?.students?.[0];
    if(first)state.selectedStudentId=first.id;

    await visit('coach-dashboard',()=>{currentProfile.role='coach';mode='coach';coachTab='dashboard';coachStudentTab='summary'});
    if(first){
      for(const tab of ['summary','routine','progress','history','tracking','nutrition']){
        await visit('coach-'+tab,()=>{currentProfile.role='coach';mode='coach';coachTab='student';coachStudentTab=tab;state.selectedStudentId=first.id});
      }
      for(const tab of ['home','tracking','nutrition','progress','history']){
        await visit('student-'+tab,()=>{currentProfile.role='student';mode='student';studentTab=tab;state.selectedStudentId=first.id});
      }
    }

    try{result.health.runtime=window.__fjzRuntimeHealthV192?.()||null}catch(e){}
    try{result.health.performance=window.__fjzPerformanceHealthV206?.()||null}catch(e){}
    try{result.health.interaction=window.__fjzInteractionHealthV193?.()||null}catch(e){}
  }catch(e){
    result.errors.push('bootstrap: '+String(e?.stack||e));
  }

  const pre=document.createElement('pre');
  pre.id='fjzGeometryAuditResult';
  pre.textContent=JSON.stringify(result);
  document.body.appendChild(pre);
})();
</script>
"""

src=INDEX.read_text(encoding="utf-8")
if "</body>" not in src:
    raise SystemExit("index missing body")
qa=src.replace("</body>",audit_js+"\n</body>",1)
qa_path=PUBLIC/"__qa_v265.html"
qa_path.write_text(qa,encoding="utf-8")

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

os.chdir(PUBLIC)
server=socketserver.TCPServer(("127.0.0.1",0),Quiet)
port=server.server_address[1]
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()

viewports=[(1440,1000),(1024,900),(768,900),(600,900),(500,900),(500,700)]
reports=[]
try:
    for w,h in viewports:
        profile=tempfile.mkdtemp(prefix="fjz-chrome-")
        cmd=[
            chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
            "--disable-background-networking","--hide-scrollbars",
            f"--window-size={w},{h}",f"--user-data-dir={profile}",
            "--virtual-time-budget=7000","--dump-dom",
            f"http://127.0.0.1:{port}/__qa_v265.html"
        ]
        cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=35)
        m=re.search(r'<pre id="fjzGeometryAuditResult">(.*?)</pre>',cp.stdout,re.S)
        if not m:
            print("CHROME STDERR",cp.stderr[-3000:])
            raise SystemExit(f"V20.65 browser audit result missing at {w}x{h}")
        payload=json.loads(htmlmod.unescape(m.group(1)))
        reports.append(payload)
finally:
    server.shutdown();server.server_close()
    try: qa_path.unlink()
    except Exception: pass

failures=[]
for rep in reports:
    vp=f"{rep['viewport']['w']}x{rep['viewport']['h']}"
    if rep.get("errors"): failures.append({"viewport":vp,"type":"js_errors","items":rep["errors"]})
    for view in rep.get("views",[]):
        if view.get("docOverflow",0)>2:
            failures.append({"viewport":vp,"view":view["name"],"type":"document_overflow","value":view["docOverflow"]})
        if view.get("overflow"):
            failures.append({"viewport":vp,"view":view["name"],"type":"structural_overflow","items":view["overflow"][:8]})
        if view.get("controls"):
            failures.append({"viewport":vp,"view":view["name"],"type":"control_overflow","items":view["controls"][:8]})
        if view.get("geometryTransitions"):
            failures.append({"viewport":vp,"view":view["name"],"type":"geometry_transition","items":view["geometryTransitions"][:8]})
        if view.get("shifts"):
            failures.append({"viewport":vp,"view":view["name"],"type":"settle_shift","items":view["shifts"][:8]})
        if view.get("renderMs",0)>350:
            failures.append({"viewport":vp,"view":view["name"],"type":"slow_render_ms","value":view["renderMs"]})
        if view.get("activeAnimations",0)>3:
            failures.append({"viewport":vp,"view":view["name"],"type":"active_animations","value":view["activeAnimations"]})

summary={
    "viewports":[r["viewport"] for r in reports],
    "views_per_viewport":[len(r.get("views",[])) for r in reports],
    "max_render_ms":max((v.get("renderMs",0) for r in reports for v in r.get("views",[])),default=0),
    "failures":failures
}
print("TEAM FJZ V20.65 BROWSER GEOMETRY AUDIT")
print(json.dumps(summary,indent=2,ensure_ascii=False))
if failures:
    raise SystemExit("V20.65 browser geometry/stability failures detected")
print("TEAM FJZ V20.65 BROWSER GEOMETRY AUDIT OK")
