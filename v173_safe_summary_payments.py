import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v173SafeSummaryPaymentsStyles">
/* Safety net: the old V6.3 card must never be visible again. */
#v63UnifiedSummary{display:none!important}

/* Keep the canonical V17 summary compact: identity and detailed check-in already live elsewhere. */
#v170SummaryGrid .v170-summary-metric:nth-child(1),
#v170SummaryGrid .v170-summary-metric:nth-child(3),
#v170SummaryGrid .v170-summary-metric:nth-child(7),
#v170SummaryGrid .v170-summary-metric:nth-child(8){
  display:none!important
}
#v170CoachOverview .v170-overview-actions{display:none!important}
#v170SummaryGrid{
  grid-template-columns:repeat(4,minmax(0,1fr))!important
}
#v170CoachOverview{
  contain:layout style
}

/* Cobranzas: clear way back + cleaner hero/actions. */
.v173-payments-hero{
  align-items:center!important;
  margin-bottom:14px!important
}
.v173-payments-actions{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:8px;
  flex-wrap:wrap
}
#v173PaymentsBack{
  min-width:128px
}
#v122PaymentsBody .v122-grid{
  gap:9px!important
}
#v122PaymentsBody .v122-row{
  min-width:0
}
@media(max-width:760px){
  #v170SummaryGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .v173-payments-hero{align-items:flex-start!important}
  .v173-payments-actions{
    width:100%;
    display:grid;
    grid-template-columns:1fr 1fr
  }
  .v173-payments-actions .btn{width:100%}
}
</style>
"""

js=r"""
<script id="v173SafeSummaryPaymentsRuntime">
(function(){
  const VERSION='17.3';

  function removeLegacySummaryV173(){
    try{document.getElementById('v63UnifiedSummary')?.remove()}catch(e){}
  }

  // IMPORTANT: do not delete the legacy symbol. Older wrappers still reference it.
  // Replace it with a harmless no-op so those references stay valid but do no work.
  const noLegacySummaryV173=async function(){
    removeLegacySummaryV173();
    return null;
  };
  try{
    window.injectUnifiedStudentSummaryV63=noLegacySummaryV173;
    injectUnifiedStudentSummaryV63=noLegacySummaryV173;
  }catch(e){
    window.injectUnifiedStudentSummaryV63=noLegacySummaryV173;
  }

  function enhancePaymentsV173(){
    if(!(currentProfile?.role==='coach'&&coachTab==='payments'))return;
    const hero=el('view')?.querySelector('.hero');
    if(!hero)return;

    hero.classList.add('v173-payments-hero');
    let actions=hero.querySelector('.pill-row');
    if(!actions){
      actions=document.createElement('div');
      actions.className='pill-row';
      hero.appendChild(actions);
    }
    actions.classList.add('v173-payments-actions');

    if(!el('v173PaymentsBack')){
      const back=document.createElement('button');
      back.id='v173PaymentsBack';
      back.type='button';
      back.className='btn ghost';
      back.textContent='← Panel Coach';
      back.addEventListener('click',()=>{
        coachTab='dashboard';
        render();
      });
      actions.prepend(back);
    }
  }

  const basePaymentsV173=window.renderCoachPaymentsV122;
  if(typeof basePaymentsV173==='function'){
    window.renderCoachPaymentsV122=async function(){
      const out=await basePaymentsV173.apply(this,arguments);
      enhancePaymentsV173();
      return out;
    };
  }

  // Existing render chain can call the legacy V6.3 hook after a screen draw.
  // This cleanup is synchronous and contains no data request or observer.
  const baseRenderV173=window.render;
  window.render=function(){
    const out=baseRenderV173.apply(this,arguments);
    removeLegacySummaryV173();
    if(currentProfile?.role==='coach'&&coachTab==='payments')enhancePaymentsV173();
    return out;
  };

  removeLegacySummaryV173();

  window.__fjzSafeUiV173={
    version:VERSION,
    legacySummarySymbolPreserved:true,
    legacySummaryNoOp:true,
    noExtraSummaryQueries:true,
    canonicalSummaryOnly:true,
    compactSummary:true,
    paymentsBackNavigation:true,
    isolatedPatch:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzSafeUiV173",
  "legacySummarySymbolPreserved:true",
  "legacySummaryNoOp:true",
  "noExtraSummaryQueries:true",
  "canonicalSummaryOnly:true",
  "paymentsBackNavigation:true",
  "isolatedPatch:true"
]:
    if marker not in html:
        raise RuntimeError("V17.3 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V17.3 safe summary dedup/payments navigation enabled")
