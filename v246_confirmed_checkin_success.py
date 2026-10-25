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
    if not m: raise RuntimeError("V20.46 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.46 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-student-action-hub" content="20.45"',
    "canonicalCheckin:true",
    "La nube no confirmó el check-in.",
    "weekly_checkins"
]:
    if marker not in html:
        raise RuntimeError("V20.46 missing prerequisite: "+marker)

def patch_v170(body):
    submit_anchor="  window.submitWeeklyCheckin=async function(){"
    if body.count(submit_anchor)!=1:
        raise RuntimeError("V20.46 submit authority mismatch: "+str(body.count(submit_anchor)))

    helper=r"""
  function showConfirmedCheckinV246(row){
    const week=row?.week_start||'';
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon success">✓</div>'+
        '<div class="v207-save-title">Check-in guardado con éxito</div>'+
        '<div class="v207-save-copy">La nube confirmó tu check-in'+
          (week?' de la semana '+esc(week):'')+
          '. Tu coach ya puede revisarlo.</div>'+
        '<div class="v207-save-actions">'+
          '<button class="btn" onclick="closeModal()">Listo</button>'+
          '<button class="btn primary" onclick="closeModal();studentTab=\\'progress\\';render()">Ver progreso</button>'+
        '</div>'+
      '</div>'
    );
  }

"""
    body=body.replace(submit_anchor,helper+submit_anchor,1)

    old_success="""      student().checkin='Recibido';saveState();trackingLoadedFor=null;await loadTracking(true);dedupPhotosV170();renderStudentTrackingHistory();
      editingCheckinWeek='';clearCheckinV170();renderSentStateV170();toast('Check-in enviado');"""
    new_success="""      // Supabase already confirmed the persisted weekly_checkins row.
      student().checkin='Recibido';
      saveState();

      editingCheckinWeek='';
      clearCheckinV170();

      trackingLoadedFor=null;
      try{
        await loadTracking(true);
        dedupPhotosV170();
        renderStudentTrackingHistory();
      }catch(refreshErr){
        console.warn('TEAM FJZ V20.46 check-in refresh after confirmed save',refreshErr);
        try{
          trackingCache.checkins=Array.isArray(trackingCache?.checkins)
            ?[data,...trackingCache.checkins.filter(x=>x?.id!==data.id&&x?.week_start!==data.week_start)]
            :[data];
        }catch(_e){}
      }

      renderSentStateV170();
      showConfirmedCheckinV246(data);"""
    if body.count(old_success)!=1:
        raise RuntimeError("V20.46 confirmed success block mismatch: "+str(body.count(old_success)))
    body=body.replace(old_success,new_success,1)

    marker_old="window.__fjzRuntimeV170={version:VERSION,consolidated:true,obsoleteRuntimeBlocksRemoved:19,canonicalDashboard:true,canonicalSummary:true,canonicalCheckin:true,alertReinjectCoalesced:true,photoDedup:true};"
    marker_new="window.__fjzRuntimeV170={version:VERSION,consolidated:true,obsoleteRuntimeBlocksRemoved:19,canonicalDashboard:true,canonicalSummary:true,canonicalCheckin:true,alertReinjectCoalesced:true,photoDedup:true,confirmedCheckinSuccess:true,checkinSuccessOnlyAfterCloudConfirmation:true,checkinRefreshFailureCannotMaskConfirmedSave:true};"
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.46 runtime marker mismatch")
    body=body.replace(marker_old,marker_new,1)

    return body

html=edit_script(html,"v170ConsolidatedRuntime",patch_v170)

html=html.replace("</head>",'<meta name="fjz-confirmed-checkin-success" content="20.46">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.46 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-confirmed-checkin-success" content="20.46"',
    "showConfirmedCheckinV246",
    "Check-in guardado con éxito",
    "La nube confirmó tu check-in",
    "confirmedCheckinSuccess:true",
    "checkinSuccessOnlyAfterCloudConfirmation:true",
    "checkinRefreshFailureCannotMaskConfirmedSave:true",
    "La nube no confirmó el check-in."
]:
    if marker not in html:
        raise RuntimeError("V20.46 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.46 confirmed check-in success")
print("V20.46 BEFORE:",before)
print("V20.46 AFTER:",after)
print("V20.46 success modal only after confirmed Supabase write")
