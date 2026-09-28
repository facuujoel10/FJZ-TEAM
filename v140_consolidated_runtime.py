import pathlib,re
from html.parser import HTMLParser
from collections import Counter

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# ---------- 1) Remove obsolete release work from V12.4 ----------
# Central release authority rewrites all version constants/labels at build time.
html,n_norm=re.subn(
    r"  function normalizeVersionV124\(\)\{.*?\n  \}\n",
    "  function normalizeVersionV124(){}\n",
    html,count=1,flags=re.S
)

html=html.replace("    setTimeout(normalizeVersionV124,100);\n","")
html=html.replace("  document.addEventListener('DOMContentLoaded',normalizeVersionV124,{once:true});\n","")
html=html.replace("  setTimeout(normalizeVersionV124,150);\n","")

# Export the useful admin injection and remove its dedicated render wrapper.
admin_fn_end="""    hero.insertAdjacentElement('afterend',card);
  }
"""
if admin_fn_end in html and "window.__fjzInjectCoachAdminV124" not in html:
    html=html.replace(admin_fn_end,admin_fn_end+"\n  window.__fjzInjectCoachAdminV124=injectCoachAdminCardV124;\n",1)

html,n_admin_wrap=re.subn(
    r"""  const previousRenderV124=render;\n  render=function\(\)\{\n    const out=previousRenderV124\.apply\(this,arguments\);\n    setTimeout\(injectCoachAdminCardV124,60\);\n    return out;\n  \};\n""",
    "",
    html,count=1
)

# If the historical wrapper still contains normalizeVersion in a slightly
# different shape, remove it with a broader exact-scope fallback.
if n_admin_wrap==0:
    html,n_admin_wrap=re.subn(
        r"""  const previousRenderV124=render;\s*render=function\(\)\{\s*const out=previousRenderV124\.apply\(this,arguments\);.*?return out;\s*\};\s*""",
        "",
        html,count=1,flags=re.S
    )

# Fix the old payments empty-state scope bug while we're consolidating.
old_payment="""      const body=el('v122PaymentsBody');
      if(body&&!followupCacheV122?.payments?.length&&!body.querySelector('.v124-empty')){
        const empty=body.querySelector('.empty');
        if(empty){
          empty.className='v124-empty';
          empty.innerHTML='<strong>No hay cobranzas cargadas</strong><div style="margin-top:5px">Tocá “+ Cobranza” para elegir un alumno, fecha e importe.</div>';
        }
      }
"""
new_payment="""      const body=el('v122PaymentsBody');
      if(body&&!body.querySelector('.v122-row')&&!body.querySelector('.v124-empty')){
        const empty=[...body.querySelectorAll('.empty')].find(x=>/Todavía no cargaste cobranzas|No hay cobranzas/i.test(x.textContent||''))||body.querySelector('.empty');
        if(empty){
          empty.className='v124-empty';
          empty.innerHTML='<strong>No hay cobranzas cargadas</strong><div style="margin-top:5px">Tocá “+ Cobranza” para elegir un alumno, fecha e importe.</div>';
        }
      }
"""
if old_payment in html:
    html=html.replace(old_payment,new_payment,1)

# ---------- 1b) Move legacy profile/layout guards into the final V14 pass ----------
# V11.9: observer + render wrapper -> one exported cleanup function.
legacy_marker = """  // Remove legacy nodes immediately if an older delayed callback tries to reinsert them.
"""
if legacy_marker in html and "window.__fjzRemoveLegacyProfileV119" not in html:
    html=html.replace(
        legacy_marker,
        """  window.__fjzRemoveLegacyProfileV119=removeLegacyProfileV119;

  // V14 handles this after render; no document-wide observer required.
""",1
    )

html,n119_obs=re.subn(
    r"""  const obs=new MutationObserver\(muts=>\{.*?  obs\.observe\(document\.documentElement,\{childList:true,subtree:true\}\);\s*""",
    "",
    html,count=1,flags=re.S
)
html,n119_render=re.subn(
    r"""  const baseRenderV119=window\.render;\s*window\.render=function\(\)\{.*?return out;\s*\};\s*""",
    "",
    html,count=1,flags=re.S
)
html=html.replace("  document.addEventListener('DOMContentLoaded',removeLegacyProfileV119,{once:true});\n","")

# V12.6: keep targeted renderCoachStudent/renderCloudExtras hooks, but remove
# the general render wrapper + observer. Export its final layout pass.
post_layout_marker="""  function postLayoutV126(){
    ensureCoachProfileFirstV126();
    ensureStudentOwnDataFirstV126();
    normalizeBoxesV126();
  }
"""
if post_layout_marker in html and "window.__fjzPostLayoutV126" not in html:
    html=html.replace(
        post_layout_marker,
        post_layout_marker+"\n  window.__fjzPostLayoutV126=postLayoutV126;\n",
        1
    )

html,n126_render=re.subn(
    r"""  // Student side: place "Mis datos" first as soon as it exists\.\s*const baseRenderV126=render;\s*render=function\(\)\{.*?return out;\s*\};\s*""",
    "",
    html,count=1,flags=re.S
)
html,n126_obs=re.subn(
    r"""  // One lightweight observer only while a student summary/home is visible\.\s*let queued=false;\s*const observer=new MutationObserver\(\(\)=>\{.*?if\(view\)observer\.observe\(view,\{childList:true,subtree:false\}\);\s*""",
    "",
    html,count=1,flags=re.S
)


# ---------- 2) Export recent post-render tasks, remove their wrappers ----------
# V13.6 nutrition finalizer.
needle136="""  function ensureCoachNutritionLearnV136(){
"""
if needle136 in html and "window.__fjzPostRenderV136" not in html:
    # export after function block using the exact block tail before its render hook
    marker="""    b.insertBefore(wrap,b.firstChild);
  }

  // Final render hook: one post-render frame, no delayed timeouts.
"""
    repl="""    b.insertBefore(wrap,b.firstChild);
  }

  window.__fjzPostRenderV136=function(){
    ensureStudentNutritionNavV136();
    ensureCoachNutritionLearnV136();
  };

  // Final render hook: consolidated by V14.
"""
    html=html.replace(marker,repl,1)

html,n136=re.subn(
    r"""  const baseRenderV136=render;.*?return out;\s*\};\s*(?=// Async nutrition loaders)""",
    "",
    html,count=1,flags=re.S
)

# V13.7 routine/method finalizer.
marker137="""  // ---- interaction / background refresh stability ----
"""
if marker137 in html and "window.__fjzEnhanceCoachRoutineV137" not in html:
    html=html.replace(marker137,"  window.__fjzEnhanceCoachRoutineV137=enhanceCoachRoutineV137;\n\n"+marker137,1)

# Export deferred flush after it is declared.
flush_tail="""    }
  }

  document.addEventListener('pointerdown',()=>markInteractionV137(450),true);
"""
if flush_tail in html and "window.__fjzFlushDeferredV137" not in html:
    html=html.replace(
        flush_tail,
        """    }
  }
  window.__fjzFlushDeferredV137=flushDeferredV137;

  document.addEventListener('pointerdown',()=>markInteractionV137(450),true);
""",1
    )

html,n137=re.subn(
    r"""  const baseRenderV137=render;\s*render=function\(\)\{\s*const out=baseRenderV137\.apply\(this,arguments\);\s*fjzPostRenderV125\('routine-method-v137',enhanceCoachRoutineV137\);\s*if\(!\(currentProfile\?\.role==='student'&&studentTab==='workout'\)\)setTimeout\(flushDeferredV137,0\);\s*return out;\s*\};\s*""",
    "",
    html,count=1,flags=re.S
)

# V13.8 habits finalizer.
marker138="""  const baseRenderV138=render;
"""
if marker138 in html and "window.__fjzEnsureHabitsTabsV138" not in html:
    html=html.replace(marker138,"  window.__fjzEnsureHabitsTabsV138=ensureHabitsTabsV138;\n\n"+marker138,1)

html,n138=re.subn(
    r"""  const baseRenderV138=render;\s*render=function\(\)\{\s*const out=baseRenderV138\.apply\(this,arguments\);\s*fjzPostRenderV125\('nutrition-habits-v138',ensureHabitsTabsV138\);\s*return out;\s*\};\s*""",
    "",
    html,count=1,flags=re.S
)

# ---------- 3) Realtime + cloud reload consolidation ----------
# Core tables are already handled by the base channel. The unified channel is a
# safety net for the rest.
html=html.replace(
    """        'athlete_snapshots','athletes','weekly_checkins','body_measurements','progress_photos',""",
    """        'progress_photos',""",
    1
)
html=html.replace("Date.now()-(Number(cloudLastWrite)||0)>700","Date.now()-(Number(cloudLastWrite)||0)>1500")

# Remove layout containment from the V12.5 optimization if present.
html=re.sub(r"#view\s*\{\s*contain\s*:\s*layout\s+style\s*;?\s*\}","#view{contain:none}",html)

# ---------- 3b) V14.2 scroll contract ----------
# Remove legacy root overscroll locking. Nested panels can still scroll, but the
# document must always accept vertical wheel/touch scrolling.
html=html.replace("body{overscroll-behavior-y:none}","body{overscroll-behavior-y:auto}")
html=re.sub(r"html\s*\{([^}]*)overflow-y\s*:\s*hidden\s*;?([^}]*)\}",r"html{\1overflow-y:auto;\2}",html,flags=re.I)
html=re.sub(r"body\s*\{([^}]*)overflow-y\s*:\s*hidden\s*;?([^}]*)\}",r"body{\1overflow-y:auto;\2}",html,flags=re.I)

# ---------- 4) V14 consolidated runtime ----------
css=r"""
<style id="v140ConsolidatedLayout">
*,*::before,*::after{box-sizing:border-box}
/* V14.2 scroll contract: document owns vertical scrolling. */
html{
  scrollbar-gutter:stable;
  width:100%;
  min-height:100%;
  overflow-x:hidden!important;
  overflow-y:auto!important;
  overscroll-behavior-y:auto!important;
}
body{
  width:100%;
  min-height:100vh;
  overflow-x:hidden!important;
  overflow-y:visible!important;
  overscroll-behavior-y:auto!important;
  touch-action:pan-x pan-y;
}
.app,.shell,#view{height:auto!important;max-height:none!important}

#view,#coachStudentBody,#studentSubBody,.app-shell,.main,.content{min-width:0;max-width:100%}
.card,.hero,.metric,.option-card,.student-row,.exercise-row,.day-card,.invite-card,
.v114-profile-card,.v115-profile-card,.v122-row,.v132-step,.v136-learn-card,.v138-habit-card{
  min-width:0;max-width:100%;box-sizing:border-box;transform:none!important
}
.card,.hero,.metric,.option-card,.student-row,.exercise-row,.day-card{
  transition:border-color .12s ease,box-shadow .12s ease,background-color .12s ease!important
}
.grid,.grid.two,.metric-grid,.form-grid,.v114-profile-grid,.v115-profile-grid,
.v122-grid,.v132-assistant-top,.v136-learn-grid,.v138-habit-grid,.v138-general-list{
  min-width:0;align-items:stretch
}
.grid>*,.grid.two>*,.metric-grid>*,.form-grid>*,.v114-profile-grid>*,
.v115-profile-grid>*,.v122-grid>*,.v132-assistant-top>*,.v136-learn-grid>*,
.v138-habit-grid>*,.v138-general-list>*{min-width:0}
.input,input,select,textarea,button{max-width:100%}
.input,input,select,textarea{min-width:0}
img,video,svg,canvas{max-width:100%}
.section-title{min-width:0;align-items:flex-start}
.section-title>*{min-width:0}
.section-title h1,.section-title h2,.section-title h3,.section-title p,
.card h1,.card h2,.card h3,.card p,.card strong,.card span{overflow-wrap:anywhere}
.tabs,.v70-recipe-tabs,.v136-nutrition-tabs{
  min-width:0;
  overflow-x:auto;
  overflow-y:hidden;
  overscroll-behavior-y:auto;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:thin
}
.pill-row,.day-actions,.exercise-actions,.nutrition-builder-actions,.modal-actions{flex-wrap:wrap}
.modal,.modal-card,.modal-content{max-width:min(94vw,760px)}
@media(min-width:900px){#coachStudentBody,#studentSubBody{min-height:620px}}
@media(max-width:760px){
  .grid.two,.v114-profile-grid,.v115-profile-grid,.v132-assistant-top,
  .v136-learn-grid,.v138-habit-grid,.v138-general-list{grid-template-columns:1fr!important}
}
</style>
"""

js=r"""
<script id="v140ConsolidatedRuntime">
(function(){
  const RELEASE='14.0';

  // One coalesced cloud reload path.
  const baseRefreshV140=refreshCloudFromRealtime;
  let inFlight=false,queued=false,timer=null,lastRun=0;
  refreshCloudFromRealtime=async function(){
    if(window.__fjzShouldDeferRefreshV137?.()){
      window.__fjzDeferredCloudRefreshV137=true;
      return;
    }
    const now=Date.now(),gap=1200;
    if(inFlight){queued=true;return}
    if(now-lastRun<gap){
      queued=true;
      clearTimeout(timer);
      timer=setTimeout(()=>{timer=null;refreshCloudFromRealtime()},Math.max(80,gap-(now-lastRun)));
      return;
    }
    inFlight=true;
    try{
      await baseRefreshV140.apply(this,arguments);
      lastRun=Date.now();
    }finally{
      inFlight=false;
      if(queued){
        queued=false;
        clearTimeout(timer);
        timer=setTimeout(()=>{timer=null;refreshCloudFromRealtime()},650);
      }
    }
  };

  const UNIQUE_IDS=[
    'cloudInviteCard','v114ProfileCard','v115StudentProfileCard','v71CoachHelp',
    'v96CoachAlerts','v122PaymentsBody','v136NutritionTabs','v138NutritionTabs',
    'v94SuppStudent','v94SuppCoach','v66CoachHabits','v66StudentHabits',
    'v136CoachLearnLink','v137MethodCoachBox','v124CoachAdminCard'
  ];

  function finalPass(){
    window.__fjzRemoveLegacyProfileV119?.();
    window.__fjzPostLayoutV126?.();
    window.__fjzInjectCoachAdminV124?.();
    window.__fjzPostRenderV136?.();
    window.__fjzEnhanceCoachRoutineV137?.();
    window.__fjzEnsureHabitsTabsV138?.();

    UNIQUE_IDS.forEach(id=>{
      const nodes=[...document.querySelectorAll('#'+CSS.escape(id))];
      nodes.slice(1).forEach(n=>n.remove());
    });

    if(window.__fjzV138?.textOnlyStudentHabits){
      document.querySelectorAll('#v66StudentHabits').forEach(n=>{n.style.display='none'});
    }

    if(!(currentProfile?.role==='student'&&studentTab==='workout')){
      window.__fjzFlushDeferredV137?.();
    }
  }

  // One final wrapper replaces four recent wrappers.
  const baseRenderV140=render;
  render=function(){
    const out=baseRenderV140.apply(this,arguments);
    fjzPostRenderV125('final-v140',finalPass);
    return out;
  };

  window.__fjzFinalQA={
    version:RELEASE,
    consolidatedRuntime:true,
    cloudRefreshMinGapMs:1200,
    duplicateCleanup:true,
    layoutContract:true,
    documentScrollContract:true,
    getStatus(){
      return {
        version:window.__FJZ_RELEASE__||RELEASE,
        realtime:window.__fjzRealtimeV132?.status||'unknown',
        channels:typeof supabaseClient?.getChannels==='function'?supabaseClient.getChannels().length:null,
        pendingSync:!!localStorage.getItem('fjz_v112_pending_sync'),
        deferredRefresh:!!window.__fjzDeferredCloudRefreshV137
      };
    }
  };

  fjzPostRenderV125('final-v140-init',finalPass);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# ---------- 5) Consolidate CSS blocks ----------
# Keeping exact CSS order preserves cascade while reducing DOM nodes.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group('attrs') or ''
    # All project style blocks are ordinary styles. Keep any media/nonce-scoped
    # style separate if one ever appears.
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):
        continue
    mergeable.append(m)

if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group('attrs') or '',re.I)
        name=ident.group(1) if ident else 'anonymous'
        chunks.append(f"\n/* --- {name} --- */\n"+m.group('body').strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    merged='<style id="fjzConsolidatedStyles">'+''.join(chunks)+'\n</style>'
    html=html.replace("</head>",merged+"\n</head>",1)

# ---------- 6) Final build audit ----------
class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.scripts=0; self.styles=0
    def handle_starttag(self,tag,attrs):
        if tag=='script': self.scripts+=1
        if tag=='style': self.styles+=1
        for k,v in attrs:
            if k=='id' and v:self.ids.append(v)

parser=AuditParser();parser.feed(html)
counts=Counter(parser.ids)
dupes={k:v for k,v in counts.items() if v>1}

metrics={
  'bytes':len(html.encode('utf-8')),
  'scripts':parser.scripts,
  'styles':parser.styles,
  'static_duplicate_ids':len(dupes),
  'mutation_observers':html.count('new MutationObserver'),
  'timeouts':html.count('setTimeout('),
  'render_assignments':html.count('render=function'),
  'channels':html.count('.channel('),
}

if dupes:
    critical={k:v for k,v in dupes.items() if k in {
      'cloudInviteCard','v114ProfileCard','v115StudentProfileCard','v71CoachHelp',
      'v96CoachAlerts','v136NutritionTabs','v138NutritionTabs'
    }}
    if critical: raise RuntimeError("V14 critical duplicate ids: "+repr(critical))

for marker in [
    "consolidatedRuntime:true",
    "window.__fjzPostRenderV136",
    "window.__fjzEnhanceCoachRoutineV137",
    "window.__fjzEnsureHabitsTabsV138",
    "window.__fjzInjectCoachAdminV124",
    "window.__fjzRemoveLegacyProfileV119",
    "window.__fjzPostLayoutV126",
]:
    if marker not in html: raise RuntimeError("V14 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.0 CONSOLIDATED:",metrics)
print("V14 wrapper removals:",{"v119_observer":n119_obs,"v119_render":n119_render,"v124":n_admin_wrap,"v126_render":n126_render,"v126_observer":n126_obs,"v136":n136,"v137":n137,"v138":n138,"old_normalizer":n_norm})
print("V14 merged style blocks:",len(mergeable),"remaining styles:",parser.styles)
