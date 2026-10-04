import pathlib,re
from html.parser import HTMLParser
from collections import Counter

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
      "bytes":len(doc.encode("utf-8")),
      "scripts":len(re.findall(r"<script\b",doc,re.I)),
      "styles":len(re.findall(r"<style\b",doc,re.I)),
      "render_assignments":len(re.findall(r"(?:window\.)?render\s*=\s*function",doc)),
      "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
      "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
      "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
      "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
      "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
    }

before=metrics(html)

css=r"""
<style id="v194FinalUiSymmetryStyles">
/* =========================================================
   V19.4 · FINAL MODAL / FORM / ACTION SYMMETRY
   ========================================================= */

/* One modal geometry across the app. Library modals get a little more room,
   ordinary editors remain compact. */
.modal-wrap.v155-scroll-shell>.modal{
  width:min(620px,100%)!important;
  max-width:620px!important;
  min-width:0!important;
  box-sizing:border-box!important;
  border-radius:16px!important;
  overflow-x:hidden!important;
}
.modal-wrap.v155-scroll-shell>.modal.v155-library-modal{
  width:min(720px,100%)!important;
  max-width:720px!important;
}

.modal .modal-head{
  display:flex!important;
  align-items:flex-start!important;
  justify-content:space-between!important;
  gap:12px!important;
  min-width:0!important;
  min-height:34px!important;
  margin-bottom:12px!important;
  box-sizing:border-box!important;
}
.modal .modal-head>div{
  flex:1 1 auto!important;
  min-width:0!important;
}
.modal .modal-head h3{
  margin:0!important;
  line-height:1.22!important;
  overflow-wrap:anywhere!important;
}
.modal .modal-head .muted{
  margin-top:4px;
  line-height:1.35;
}
.modal .modal-head>.btn,
.modal .modal-head>button.btn{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  flex:0 0 34px!important;
  width:34px!important;
  min-width:34px!important;
  max-width:34px!important;
  height:34px!important;
  min-height:34px!important;
  max-height:34px!important;
  padding:0!important;
  margin:0!important;
  border-radius:10px!important;
  box-sizing:border-box!important;
  line-height:1!important;
}

/* Modal forms: two equal columns, span2 always owns the full row. */
.modal .form-grid{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;
  align-items:start!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}
.modal .form-grid>*{
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}
.modal .form-grid>.span2,
.modal .form-grid>label.span2{
  grid-column:1/-1!important;
}
.modal .form-grid>label{
  display:flex!important;
  flex-direction:column!important;
  justify-content:flex-start!important;
  gap:5px!important;
  width:100%!important;
  min-width:0!important;
  margin:0!important;
  line-height:1.3!important;
  overflow:visible!important;
}
.modal .form-grid>label>.input,
.modal .form-grid>label>input,
.modal .form-grid>label>select,
.modal input.input:not([type="file"]):not([type="checkbox"]):not([type="radio"]),
.modal select.input{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
}
.modal textarea.input{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:92px!important;
  height:auto!important;
  max-height:none!important;
  margin:0!important;
  box-sizing:border-box!important;
}
.modal input[type="file"].input{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:42px!important;
  box-sizing:border-box!important;
}

/* Modal actions share the same visual rhythm. */
.modal>.btn[style*="width:100%"],
.modal .form-grid+.btn[style*="width:100%"],
.modal button.v155-exercise-save,
.modal button.v192-session-save-confirm{
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:44px!important;
  height:auto!important;
  padding:10px 14px!important;
  box-sizing:border-box!important;
  border-radius:11px!important;
  line-height:1.2!important;
  text-align:center!important;
  white-space:normal!important;
}
.modal .pill-row{
  gap:8px!important;
  flex-wrap:wrap!important;
  min-width:0!important;
}
.modal .library,
.modal .library-item,
.modal .card{
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}

/* Section/status labels: never let the word be larger than its box. */
.section-title>.badge,
.modal .badge,
.v170-signal,
.v110-method-badge{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:auto!important;
  min-width:max-content!important;
  max-width:100%!important;
  min-height:24px!important;
  height:auto!important;
  padding:5px 9px!important;
  box-sizing:border-box!important;
  line-height:1.1!important;
  white-space:nowrap!important;
  word-break:keep-all!important;
  overflow:visible!important;
  flex-shrink:0!important;
}

/* Prevent long text from widening cards or grids. */
.card,.hero,.section-title,.modal,.modal-head,
.grid>*,.form-grid>*,.student-row>*,.track-row>*{
  min-width:0;
}
.card strong,.card p,.card .muted,.modal strong,.modal p,.modal .muted{
  overflow-wrap:anywhere;
}

@media(max-width:760px){
  .modal-wrap.v155-scroll-shell>.modal,
  .modal-wrap.v155-scroll-shell>.modal.v155-library-modal{
    width:100%!important;
    max-width:100%!important;
  }
}
@media(max-width:360px){
  .modal .form-grid{
    gap:8px!important;
  }
}
</style>
"""

js=r"""
<script id="v194AuthFreshnessRuntime">
(function(){
  const VERSION='19.4';
  let refreshPromiseV194=null;
  let lastCheckV194=0;

  async function ensureFreshAuthV194(force){
    if(!window.supabaseClient?.auth)return true;
    const now=Date.now();
    if(!force&&now-lastCheckV194<15000)return true;
    lastCheckV194=now;

    try{
      const {data,error}=await supabaseClient.auth.getSession();
      if(error)throw error;
      const session=data?.session;
      if(!session)return false;

      const expiresAt=Number(session.expires_at||0)*1000;
      if(!force&&expiresAt-now>90000)return true;

      if(!refreshPromiseV194){
        refreshPromiseV194=(async()=>{
          const {data:refreshed,error:refreshError}=await supabaseClient.auth.refreshSession();
          if(refreshError)throw refreshError;
          return !!refreshed?.session;
        })().catch(e=>{
          console.warn('TEAM FJZ V19.4 auth refresh',e);
          return false;
        }).finally(()=>{refreshPromiseV194=null});
      }
      return await refreshPromiseV194;
    }catch(e){
      console.warn('TEAM FJZ V19.4 auth preflight',e);
      return false;
    }
  }

  function wrapCloudTaskV194(name){
    const fn=window[name]||globalThis[name];
    if(typeof fn!=='function'||fn.__v194AuthWrapped)return false;
    const wrapped=async function(){
      await ensureFreshAuthV194(false);
      return fn.apply(this,arguments);
    };
    wrapped.__v194AuthWrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
    return true;
  }

  const wrappedTasks=[
    'syncCloudNow',
    'refreshCloudFromRealtime',
    'loadCoachCloud',
    'loadStudentCloud'
  ].filter(wrapCloudTaskV194);

  window.addEventListener('online',()=>{ensureFreshAuthV194(true)},{passive:true});
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible')ensureFreshAuthV194(false);
  },{passive:true});

  window.__fjzEnsureFreshAuthV194=ensureFreshAuthV194;
  window.__fjzV194={
    version:VERSION,
    modalGeometryUnified:true,
    modalFormSymmetry:true,
    staticDuplicateIdAudit:true,
    authExpiryPreflight:true,
    wrappedCloudTasks:wrappedTasks
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# ---------------------------------------------------------
# Final stylesheet consolidation; preserve cascade order.
# ---------------------------------------------------------
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)

if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV194">'+''.join(chunks)+'\n</style>\n</head>',1)

# ---------------------------------------------------------
# Static DOM audit: actual document IDs only (script strings excluded).
# ---------------------------------------------------------
class StaticIdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k.lower()=="id" and v:self.ids.append(v)

parser=StaticIdParser()
parser.feed(html)
dups={k:v for k,v in Counter(parser.ids).items() if v>1}
if dups:
    raise RuntimeError("V19.4 duplicate static DOM ids: "+repr(dups))

after=metrics(html)

critical=[
  "__fjzConfirmSessionSavedV190",
  "__fjzInteractionHealthV193",
  "__fjzRuntimeHealthV192",
  "window.submitWeeklyCheckin",
  "window.saveMeasurementV176",
  "window.renderNutritionStudentLoaded",
  "deleteSessionV148",
  "deleteDayV152",
  "window.__fjzShouldRenderRealtimeV146",
  "v194AuthFreshnessRuntime",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V19.4 critical functionality missing: "+repr(missing))

if after["styles"]!=1:
    raise RuntimeError("V19.4 expected one final stylesheet, got "+str(after["styles"]))
if after["render_assignments"]>23:
    raise RuntimeError("V19.4 render wrapper regression: "+str(after["render_assignments"]))
if after["mutation_observers"]>3:
    raise RuntimeError("V19.4 observer regression: "+str(after["mutation_observers"]))
if after["performance_observers"]!=0:
    raise RuntimeError("V19.4 PerformanceObserver regression")
if after["timeouts"]>52:
    raise RuntimeError("V19.4 timer regression: "+str(after["timeouts"]))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.4 FINAL AUDIT BEFORE:",before)
print("TEAM FJZ V19.4 FINAL AUDIT AFTER:",after)
print("TEAM FJZ V19.4 static DOM IDs:",len(parser.ids),"duplicates:",dups)
print("TEAM FJZ V19.4 modal symmetry + auth freshness enabled")
