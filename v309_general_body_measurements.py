import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    "arm_left_cm",
    "arm_right_cm",
    "thigh_left_cm",
    "thigh_right_cm",
    "window.simpleLineChart",
    "openEditMeasurementV176",
]:
    if marker not in html:
        raise RuntimeError("V21.09 prerequisite missing "+marker)

runtime=r"""
<script id="v309GeneralBodyMeasurementsRuntime">
(function(){
  const VERSION='21.09';

  function firstMeasureV309(a,b){
    const na=Number(a),nb=Number(b);
    if(a!=null&&a!==''&&Number.isFinite(na))return na;
    if(b!=null&&b!==''&&Number.isFinite(nb))return nb;
    return null;
  }

  function normalizeMeasurementV309(m){
    if(!m||typeof m!=='object')return m;
    const arm=firstMeasureV309(m.arm_left_cm,m.arm_right_cm);
    const thigh=firstMeasureV309(m.thigh_left_cm,m.thigh_right_cm);
    if(arm!=null)m.arm_left_cm=arm;
    if(thigh!=null)m.thigh_left_cm=thigh;
    return m;
  }

  function normalizeTrackingMeasurementsV309(){
    try{
      if(Array.isArray(trackingCache?.measurements)){
        trackingCache.measurements.forEach(normalizeMeasurementV309);
      }
    }catch(_e){}
  }

  const baseSimpleV309=window.simpleLineChart;
  window.simpleLineChart=function(rows,key,label){
    const k=String(key||'');
    if(k==='arm_right_cm'||k==='thigh_right_cm')return '';
    if(k==='arm_left_cm'){
      const xs=(rows||[]).map(x=>({...x,arm_left_cm:firstMeasureV309(x?.arm_left_cm,x?.arm_right_cm)}));
      return baseSimpleV309?.call(this,xs,'arm_left_cm','Brazo')||'';
    }
    if(k==='thigh_left_cm'){
      const xs=(rows||[]).map(x=>({...x,thigh_left_cm:firstMeasureV309(x?.thigh_left_cm,x?.thigh_right_cm)}));
      return baseSimpleV309?.call(this,xs,'thigh_left_cm','Muslo')||'';
    }
    return baseSimpleV309?.apply(this,arguments);
  };
  try{simpleLineChart=window.simpleLineChart}catch(_e){}

  function exactTextV309(v){
    return String(v||'').replace(/\s+/g,' ').trim().toLowerCase();
  }

  function removeLegacySideNodeV309(node){
    if(!node||!node.isConnected)return;
    const holder=node.closest(
      '.v94-chart,.v205-chart,.v93-measure-item,.v93-measure-card,.metric,label,.form-field,.field,.measure-field'
    );
    if(holder&&holder!==document.body){
      holder.remove();
      return;
    }
    node.remove();
  }

  function renameTextNodesV309(root){
    if(!root)return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    const replacements=[];
    while(walker.nextNode()){
      const n=walker.currentNode,t=n.nodeValue||'';
      if(/brazo\s+(izquierdo|izq\.?)/i.test(t))replacements.push([n,t.replace(/brazo\s+(izquierdo|izq\.?)/ig,'Brazo')]);
      if(/muslo\s+(izquierdo|izq\.?)/i.test(t))replacements.push([n,t.replace(/muslo\s+(izquierdo|izq\.?)/ig,'Muslo')]);
    }
    replacements.forEach(([n,v])=>{n.nodeValue=v});
  }

  function cleanupSideSpecificMeasurementUIV309(){
    normalizeTrackingMeasurementsV309();
    const activeCoach=currentProfile?.role==='coach'&&coachTab==='student'&&['progress','tracking','summary'].includes(coachStudentTab);
    const activeStudent=currentProfile?.role==='student'&&mode==='student'&&['progress','tracking','home'].includes(studentTab);
    if(!activeCoach&&!activeStudent)return;
    const root=activeCoach?(el('coachStudentBody')||el('view')):(el('studentSubBody')||el('view'));
    if(!root)return;

    root.querySelectorAll('label,.metric,.v94-chart,.v205-chart,.v93-measure-item,.v93-measure-card,.form-field,.field,.measure-field').forEach(node=>{
      const t=exactTextV309(node.textContent);
      if(/^(brazo|muslo)\s+(derecho|der\.?)(\s|$)/i.test(t)){
        removeLegacySideNodeV309(node);
      }
    });

    root.querySelectorAll('input,select,textarea').forEach(input=>{
      const id=String(input.id||'').toLowerCase();
      const name=String(input.name||'').toLowerCase();
      const key=id+' '+name;
      if(/(arm|brazo).*(right|derech|der\b)/i.test(key)||(thigh|muslo).*(right|derech|der\b)/i.test(key)){
        removeLegacySideNodeV309(input);
      }
    });

    renameTextNodesV309(root);
  }

  const baseEditV309=window.openEditMeasurementV176;
  window.openEditMeasurementV176=function(){
    normalizeTrackingMeasurementsV309();
    return baseEditV309?.apply(this,arguments);
  };

  const baseCompareV309=window.injectCompareV93;
  if(typeof baseCompareV309==='function'){
    window.injectCompareV93=async function(){
      normalizeTrackingMeasurementsV309();
      const out=await baseCompareV309.apply(this,arguments);
      cleanupSideSpecificMeasurementUIV309();
      return out;
    };
    try{injectCompareV93=window.injectCompareV93}catch(_e){}
  }

  const basePostV309=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    normalizeTrackingMeasurementsV309();
    const out=basePostV309?.apply(this,arguments);
    cleanupSideSpecificMeasurementUIV309();
    return out;
  };

  cleanupSideSpecificMeasurementUIV309();

  window.__fjzV309={
    version:VERSION,
    generalArmOnly:true,
    generalThighOnly:true,
    legacySideDataCompatible:true,
    rightSideUiRemoved:true,
    historicalFallbackPreserved:true,
    noDataDeletion:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-general-body-measurements" content="21.09">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.09 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-general-body-measurements" content="21.09"',
    'id="v309GeneralBodyMeasurementsRuntime"',
    "generalArmOnly:true",
    "generalThighOnly:true",
    "legacySideDataCompatible:true",
    "rightSideUiRemoved:true",
    "historicalFallbackPreserved:true",
    "noDataDeletion:true",
    "k==='arm_right_cm'||k==='thigh_right_cm'",
    "firstMeasureV309(m.arm_left_cm,m.arm_right_cm)",
    "firstMeasureV309(m.thigh_left_cm,m.thigh_right_cm)",
]:
    if marker not in html:
        raise RuntimeError("V21.09 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.09 general body measurements")
print("V21.09 BEFORE:",before)
print("V21.09 AFTER:",after)
