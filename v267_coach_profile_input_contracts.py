import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.67 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.67 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-athlete-workspace" content="20.66"',
    "canonicalCheckin:true",
    "singleExerciseSave:true",
    "measurementEdit:true",
    "confirmedCheckinSuccess:true"
]:
    if marker not in html:
        raise RuntimeError("V20.67 missing prerequisite: "+marker)

# ------------------------------------------------------------------
# 1) COACH AVATAR: bypass stale empty cache and read linked profile
#    directly under existing RLS. No policy/schema changes.
# ------------------------------------------------------------------
def patch_v175(body):
    old=re.search(r"""  async function hydrateCoachAvatarV175\(\)\{.*?\n  \}\n  const coachAvatarV175=""",body,re.S)
    if not old:
        raise RuntimeError("V20.67 coach avatar function mismatch")
    new=r"""  async function hydrateCoachAvatarV175(){
    ensureCoachHeroFrameV175();
    if(!(currentProfile?.role==='coach'&&coachTab==='student'))return;
    const hero=el('view')?.querySelector('.hero'),slot=el('v175CoachAvatarSlot'),s=student?.(),ath=coachAthleteV175();
    if(!hero||!slot||!s)return;

    const initials=esc((s.name||'AL').slice(0,2).toUpperCase());
    const setFallback=(label)=>{
      if(!el('v175CoachAvatarSlot'))return;
      el('v175CoachAvatarSlot').innerHTML='<div class="v70-avatar big">'+initials+'</div>';
      el('v175CoachAvatarSlot').dataset.photoState=label||'fallback';
    };

    if(!ath?.user_id){
      setFallback('unlinked');
      const chip=hero.querySelector('.v266-profile-state');
      if(chip&&!hero.querySelector('.v267-avatar-note')){
        chip.insertAdjacentHTML('afterend','<span class="v267-avatar-note">Cuenta sin vincular · sin foto sincronizada</span>');
      }
      return;
    }

    const key=String(s.id);
    try{
      let path='';
      if(supabaseClient){
        const {data,error}=await supabaseClient.from('profiles')
          .select('id,avatar_url')
          .eq('id',ath.user_id)
          .maybeSingle();
        if(error)throw error;
        path=data?.avatar_url||'';
        try{avatarPathCacheV70?.set?.(ath.user_id,path)}catch(_e){}
      }else{
        path=await profilePathV70?.(ath.user_id)||'';
      }

      if(!(currentProfile?.role==='coach'&&coachTab==='student'&&String(student()?.id)===key))return;
      if(!path){setFallback('empty');return}

      let url='';
      try{url=await signedAvatarV70(path)}catch(_e){}
      if(!(currentProfile?.role==='coach'&&coachTab==='student'&&String(student()?.id)===key))return;
      if(!url){setFallback('signed-url-failed');return}

      const target=el('v175CoachAvatarSlot');
      if(!target)return;
      target.innerHTML='<div class="v70-avatar big"><img src="'+url+'" alt="'+esc(s.name||'Foto del alumno')+'"></div>';
      target.dataset.photoState='loaded';
    }catch(e){
      console.warn('TEAM FJZ V20.67 coach avatar load',e);
      setFallback('error');
    }
  }
  const coachAvatarV175="""
    body=body[:old.start()]+new+body[old.end():]

    marker="""    coachProfileCommandCenter:true
  };"""
    repl="""    coachProfileCommandCenter:true,
    coachAvatarDirectLinkedProfile:true,
    coachAvatarBypassesStaleEmptyCache:true
  };"""
    if body.count(marker)!=1:
        raise RuntimeError("V20.67 avatar marker mismatch")
    return body.replace(marker,repl,1)

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ------------------------------------------------------------------
# 2) COACH PROFILE: richer athlete dossier using existing athlete fields.
# ------------------------------------------------------------------
def patch_v114(body):
    age_anchor="""  function sexLabelV114(v){
"""
    helpers=r"""  function tenureV267(date){
    if(!date)return 'Sin cargar';
    const d=new Date(date+'T12:00:00');
    if(Number.isNaN(d.getTime()))return 'Sin cargar';
    const days=Math.max(0,Math.floor((Date.now()-d.getTime())/86400000));
    if(days<31)return days+' días';
    const months=Math.floor(days/30.44);
    if(months<12)return months+' mes'+(months===1?'':'es');
    const years=Math.floor(months/12),rem=months%12;
    return years+' año'+(years===1?'':'s')+(rem?' · '+rem+' mes'+(rem===1?'':'es'):'');
  }
  function profileSignalV267(r){
    const s=student?.()||{};
    const status=statusFor?.(s)||'Seguimiento';
    const planned=Math.max(0,Number(s.plannedPerWeek)||s.days?.length||0);
    return {status,planned,adherence:Number(adherence?.(s)||0),last:s.lastWorkout||null};
  }

"""
    if body.count(age_anchor)!=1:
        raise RuntimeError("V20.67 profile helper anchor mismatch")
    body=body.replace(age_anchor,helpers+age_anchor,1)

    fn=re.search(r"""  function profileHtmlV114\(r\)\{.*?\n  \}\n\n  async function injectProfileV114""",body,re.S)
    if not fn:
        raise RuntimeError("V20.67 profileHtml mismatch")
    replacement=r"""  function profileHtmlV114(r){
    const age=ageV114(r.birth_date),sig=profileSignalV267(r);
    const account=r.user_id?'Cuenta vinculada':'Cuenta pendiente de vincular';
    const last=sig.last?fmtDate(sig.last):'Sin registro';
    return '<div class="card v114-profile-card v267-dossier" id="v114ProfileCard">'+
      '<div class="v267-dossier-head"><div><div class="v266-section-kicker">FICHA PROFESIONAL</div><h3>Datos y contexto del alumno</h3>'+
      '<p>Información personal, antigüedad y contexto útil para tomar decisiones sin salir de la ficha.</p></div>'+
      '<button class="btn small" onclick="openEditStudentProfileV114()">Editar ficha</button></div>'+
      '<div class="v267-dossier-status">'+
        '<div><span>Estado</span><strong>'+esc(sig.status)+'</strong></div>'+
        '<div><span>Adherencia</span><strong>'+sig.adherence+'%</strong></div>'+
        '<div><span>Frecuencia</span><strong>'+(sig.planned?sig.planned+'x/sem':'—')+'</strong></div>'+
        '<div><span>Último entreno</span><strong>'+esc(last)+'</strong></div>'+
      '</div>'+
      '<div class="v114-profile-grid v267-profile-grid">'+
        '<div class="v114-profile-field"><span>Edad</span><strong>'+(age!==null?age+' años':'Sin cargar')+'</strong></div>'+
        '<div class="v114-profile-field"><span>Altura</span><strong>'+esc(valV114(r.height_cm,' cm'))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Sexo</span><strong>'+esc(sexLabelV114(r.sex))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Nacimiento</span><strong>'+esc(fmtDateV114(r.birth_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Inicio del plan</span><strong>'+esc(fmtDateV114(r.start_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Antigüedad</span><strong>'+esc(tenureV267(r.start_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Ocupación / estudio</span><strong>'+esc(valV114(r.occupation_study))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Cuenta</span><strong>'+esc(account)+'</strong></div>'+
        '<div class="v114-profile-field v114-goal v267-goal"><span>Objetivo actual</span><strong>'+esc(r.goal||'Sin cargar')+'</strong></div>'+
      '</div></div>';
  }

  async function injectProfileV114"""
    body=body[:fn.start()]+replacement+body[fn.end():]
    return body

html=edit_script(html,"v114CoachProfileRuntime",patch_v114)

# ------------------------------------------------------------------
# 3) CHECK-IN: canonical score input is hard 1..10, integer only.
# ------------------------------------------------------------------
def patch_v170(body):
    old="""  function normalizeScoreV170(input,finalize=false){
    if(!input)return;let raw=String(input.value||'').replace(/[^0-9]/g,'').slice(0,2);
    if(!raw){input.value='';return}let n=parseInt(raw,10);if(n>10)n=10;if(finalize&&n<1){input.value='';return}input.value=String(n);
  }"""
    new="""  function normalizeScoreV170(input,finalize=false){
    if(!input)return;
    let raw=String(input.value||'').replace(/[^0-9]/g,'').slice(0,2);
    if(!raw){input.value='';return}
    if(raw==='0'||raw==='00'){input.value='';return}
    let n=parseInt(raw,10);
    if(!Number.isFinite(n)){input.value='';return}
    n=Math.max(1,Math.min(10,n));
    input.value=String(n);
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V20.67 checkin normalizer mismatch")
    body=body.replace(old,new,1)

    old_score="""'<input id="'+id+'" class="input v170-score-input" type="tel" inputmode="numeric" pattern="[0-9]*" maxlength="2" autocomplete="off" placeholder="—"><span>/10</span></div></div>';"""
    new_score="""'<input id="'+id+'" class="input v170-score-input" type="tel" inputmode="numeric" pattern="[1-9]|10" maxlength="2" autocomplete="off" aria-label="'+esc(label)+' del 1 al 10" placeholder="1–10"><span>/10</span></div></div>';"""
    if body.count(old_score)!=1:
        raise RuntimeError("V20.67 checkin input markup mismatch")
    body=body.replace(old_score,new_score,1)
    return body

html=edit_script(html,"v170ConsolidatedRuntime",patch_v170)

# ------------------------------------------------------------------
# 4) INPUT CONTRACTS: numeric workout/routine/tracking fields only.
#    Comments/notes/textareas stay unrestricted.
# ------------------------------------------------------------------
runtime=r"""
<script id="v267InputContractsRuntime">
(function(){
  function numberKeyV267(e,integer=false){
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    const k=e.key;
    if(['Backspace','Delete','Tab','Enter','Escape','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(k))return;
    if(/^[0-9]$/.test(k))return;
    if(!integer&&(k==='.'||k===','))return;
    e.preventDefault();
  }

  function sanitizeDecimalV267(v,integer=false){
    let s=String(v??'').replace(',','.');
    s=s.replace(integer?/[^0-9]/g:/[^0-9.]/g,'');
    if(!integer){
      const i=s.indexOf('.');
      if(i>=0)s=s.slice(0,i+1)+s.slice(i+1).replace(/\./g,'');
    }
    return s;
  }

  function hardenV267(input,opts={}){
    if(!input||input.tagName!=='INPUT')return;
    const integer=!!opts.integer;
    if(opts.min!=null)input.min=String(opts.min);
    if(opts.max!=null)input.max=String(opts.max);
    if(opts.step!=null)input.step=String(opts.step);
    input.inputMode=integer?'numeric':'decimal';
    input.autocomplete='off';
    input.dataset.v267Numeric='1';

    if(!input.__v267Key){
      const prev=input.onkeydown;
      input.onkeydown=function(e){
        numberKeyV267(e,integer);
        if(e.defaultPrevented)return false;
        if(typeof prev==='function')return prev.call(this,e);
      };
      input.__v267Key=true;
    }

    if(input.type==='text'||input.type==='tel'){
      if(!input.__v267Input){
        const prev=input.oninput;
        input.oninput=function(e){
          const clean=sanitizeDecimalV267(this.value,integer);
          if(this.value!==clean)this.value=clean;
          if(typeof prev==='function')return prev.call(this,e);
        };
        input.__v267Input=true;
      }
    }
  }

  function byIdV267(id,opts){
    const x=el(id);if(x)hardenV267(x,opts);
  }

  function applyWorkoutV267(){
    document.querySelectorAll('.session-card .set-grid label').forEach(label=>{
      const input=label.querySelector('input');if(!input)return;
      const t=(label.textContent||'').toLowerCase();
      if(/\brir\b/.test(t))hardenV267(input,{integer:true,min:0,max:10,step:1});
      else if(/rep/.test(t))hardenV267(input,{integer:true,min:0,max:999,step:1});
      else if(/kg|peso|lastre|asistencia|carga/.test(t))hardenV267(input,{integer:false,min:0,max:1000,step:.25});
    });

    document.querySelectorAll('.v137-method-step label,.session-card [class*="method"] label,.session-card [class*="drop"] label,.session-card [class*="super"] label').forEach(label=>{
      const input=label.querySelector('input');if(!input||input.type!=='number')return;
      const t=(label.textContent||'').toLowerCase();
      if(/rep/.test(t))hardenV267(input,{integer:true,min:0,max:999,step:1});
      else hardenV267(input,{integer:false,min:0,max:1000,step:.25});
    });
  }

  function applyRoutineEditorV267(){
    [
      ['fSets',{integer:true,min:1,max:20,step:1}],
      ['fRest',{integer:true,min:0,max:1800,step:5}],
      ['fMin',{integer:true,min:1,max:999,step:1}],
      ['fMax',{integer:true,min:1,max:999,step:1}],
      ['fRMin',{integer:true,min:0,max:10,step:1}],
      ['fRMax',{integer:true,min:0,max:10,step:1}],
      ['fInc',{integer:false,min:0,max:1000,step:.25}],
      ['fIncrementV150',{integer:false,min:0,max:1000,step:.25}]
    ].forEach(([id,o])=>byIdV267(id,o));

    // Exact-reps pattern (e.g. 12-10-8-8) and note/comment fields are intentionally text.
  }

  function applyTrackingV267(){
    ['ciSleep','ciHunger','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'].forEach(id=>{
      const x=el(id);if(!x)return;
      x.inputMode='numeric';x.maxLength=2;x.pattern='[1-9]|10';x.autocomplete='off';
      x.dataset.v267Score='1';
    });

    byIdV267('ciWeight',{integer:false,min:20,max:400,step:.1});
    byIdV267('mWeight',{integer:false,min:20,max:400,step:.1});
    ['mWaist','mAbd','mHip','mChest'].forEach(id=>byIdV267(id,{integer:false,min:20,max:300,step:.1}));
    byIdV267('v176MeasureWeight',{integer:false,min:20,max:400,step:.1});
    ['v176MeasureWaist','v176MeasureHip','v176MeasureChest'].forEach(id=>byIdV267(id,{integer:false,min:20,max:300,step:.1}));
    byIdV267('v176MeasureArm',{integer:false,min:10,max:100,step:.1});
    byIdV267('v176MeasureThigh',{integer:false,min:15,max:150,step:.1});
  }

  function applyProfileV267(){
    byIdV267('v114Height',{integer:false,min:100,max:250,step:.1});
    byIdV267('v115Height',{integer:false,min:100,max:250,step:.1});
  }

  function applyGenericNumberModeV267(){
    document.querySelectorAll('input[type="number"]').forEach(input=>{
      if(input.dataset.v267Numeric==='1')return;
      input.inputMode='decimal';
      input.autocomplete='off';
      // Keep each feature's own min/max/step semantics; only block exponent/sign characters.
      if(!input.__v267Key){
        const prev=input.onkeydown;
        input.onkeydown=function(e){
          numberKeyV267(e,false);
          if(e.defaultPrevented)return false;
          if(typeof prev==='function')return prev.call(this,e);
        };
        input.__v267Key=true;
      }
    });
  }

  window.__fjzApplyInputRulesV267=function(){
    applyWorkoutV267();
    applyRoutineEditorV267();
    applyTrackingV267();
    applyProfileV267();
    applyGenericNumberModeV267();
  };

  const baseShowModalV267=window.showModal;
  if(typeof baseShowModalV267==='function'){
    window.showModal=function(){
      const out=baseShowModalV267.apply(this,arguments);
      window.__fjzApplyInputRulesV267();
      return out;
    };
    try{showModal=window.showModal}catch(_e){}
  }

  window.__fjzApplyInputRulesV267();

  window.__fjzV267={
    version:'20.67',
    strictCheckinRange1to10:true,
    workoutNumericGuard:true,
    routineNumericGuard:true,
    measurementNumericGuard:true,
    profileNumericGuard:true,
    exactRepsPatternRemainsText:true,
    commentsRemainText:true,
    coachAvatarDirectLoad:true,
    richerCoachDossier:true
  };
})();
</script>
"""

# Ask the existing post-render authority to reapply rules after route renders.
def patch_v176(body):
    old="""    polishActionLabelsV176();
    if(studentTrackingActiveV176()||coachTrackingActiveV176())injectMeasurementHistoryV176();
"""
    new="""    polishActionLabelsV176();
    window.__fjzApplyInputRulesV267?.();
    if(studentTrackingActiveV176()||coachTrackingActiveV176())injectMeasurementHistoryV176();
"""
    if body.count(old)!=1:
        raise RuntimeError("V20.67 post-render input anchor mismatch")
    return body.replace(old,new,1)

html=edit_script(html,"v176MobileTrackingMealsCleanupRuntime",patch_v176)

css=r"""
/* TEAM FJZ · V20.67 COACH DOSSIER + INPUT CONTRACTS */
#v175CoachAvatarSlot{
  width:96px!important;
  height:96px!important;
  flex-basis:96px!important;
  border-radius:20px!important;
}
#v175CoachAvatarSlot .v70-avatar.big{
  width:96px!important;
  height:96px!important;
  border-radius:19px!important;
}
#v175CoachAvatarSlot img{
  width:100%;
  height:100%;
  object-fit:cover;
  object-position:center;
  display:block;
}
.v267-avatar-note{
  display:inline-flex;
  margin:7px 0 0 7px;
  color:#858b96;
  font-size:8px;
  line-height:1.3;
}
.v267-dossier{
  border-color:#30343d!important;
  background:
    linear-gradient(145deg,rgba(255,38,57,.035),transparent 42%),
    #0f1014!important;
}
.v267-dossier-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
}
.v267-dossier-head h3{
  margin:4px 0 0;
  color:#f5f6f8;
  font-size:17px;
  font-weight:920;
  letter-spacing:-.018em;
}
.v267-dossier-head p{
  margin:5px 0 0;
  color:#9298a2;
  font-size:9px;
  line-height:1.45;
}
.v267-dossier-status{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin:12px 0 3px;
}
.v267-dossier-status>div{
  min-width:0;
  padding:9px 10px;
  border:1px solid #2a2e35;
  border-radius:10px;
  background:#0d0e12;
}
.v267-dossier-status span,
.v267-profile-grid .v114-profile-field span{
  display:block;
  color:#7f8590;
  font-size:7px;
  font-weight:900;
  letter-spacing:.07em;
  text-transform:uppercase;
}
.v267-dossier-status strong{
  display:block;
  margin-top:4px;
  color:#f1f3f6;
  font-size:12px;
  line-height:1.25;
  font-weight:900;
}
.v267-profile-grid{
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
}
.v267-profile-grid .v114-profile-field{
  min-height:66px;
  padding:10px;
  background:#101116;
}
.v267-goal{
  grid-column:1/-1!important;
  min-height:auto!important;
  border-color:rgba(255,59,77,.22)!important;
  background:linear-gradient(90deg,rgba(255,38,57,.055),transparent),#101116!important;
}
.v267-goal strong{
  font-size:13px!important;
  line-height:1.45!important;
}

/* Numeric entry surfaces: clear distinction from comments/text. */
input[data-v267-numeric="1"],
input[data-v267-score="1"]{
  font-variant-numeric:tabular-nums;
}
input[data-v267-score="1"]{
  text-align:center;
  font-weight:900;
}
.session-card .set-grid input[data-v267-numeric="1"]{
  text-align:center;
  min-height:44px;
  font-size:16px;
  font-weight:850;
}
textarea.input,
textarea{
  line-height:1.45;
}

@media(max-width:900px){
  #v175CoachAvatarSlot{
    width:74px!important;height:74px!important;flex-basis:74px!important;border-radius:17px!important;
  }
  #v175CoachAvatarSlot .v70-avatar.big{
    width:74px!important;height:74px!important;border-radius:16px!important;
  }
  .v267-profile-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}
@media(max-width:620px){
  .v267-dossier-head{display:block}
  .v267-dossier-head .btn{width:100%;margin-top:10px}
  .v267-dossier-status{grid-template-columns:1fr 1fr}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.67 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-coach-profile-input-contracts" content="20.67">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.67 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-profile-input-contracts" content="20.67"',
    "coachAvatarDirectLinkedProfile:true",
    "coachAvatarBypassesStaleEmptyCache:true",
    "strictCheckinRange1to10:true",
    "workoutNumericGuard:true",
    "routineNumericGuard:true",
    "measurementNumericGuard:true",
    "exactRepsPatternRemainsText:true",
    "commentsRemainText:true",
    "richerCoachDossier:true",
    "__fjzApplyInputRulesV267"
]:
    if marker not in html:
        raise RuntimeError("V20.67 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.67 coach dossier + input contracts")
print("V20.67 BEFORE:",before)
print("V20.67 AFTER:",after)
print("V20.67 linked avatar direct-load + richer coach dossier + strict numeric input contracts; runtime topology unchanged")
