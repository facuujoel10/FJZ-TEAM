"""Integrate staging-only fixes after the legacy alert and template transforms."""
import json


def update(html):
    def replace(old, new):
        nonlocal html
        if html.count(old) != 1:
            raise RuntimeError("Unexpected staging template: " + old)
        html = html.replace(old, new)

    guard = "if(mode!=='coach'||currentProfile?.role!=='coach')return;"
    for signature in ("function renderCoachAlertsV96(){", "async function refreshCoachAlertsV96(force=true){",
                      "function injectCoachAlertPanelV96(){", "function updateCoachBellV96(){",
                      "function injectCoachNoticeCardV96(){"):
        replace(signature, signature + guard)
    # A coach preview is authenticated as coach. Never call the account-wide feed there.
    signature = "function injectAlertsV96(){"
    replace(signature, signature + """
    if(mode==='student' && currentProfile?.role==='coach'){
      for(const id of ['v96CoachAlerts','v96CoachBell','v96NoticeCoachCard'])el(id)?.remove();
      const hero=el('view')?.querySelector('.hero');
      if(hero && !el('fjzPreviewNotices')){
        const button=document.createElement('button');button.type='button';button.id='fjzPreviewNotices';
        button.className='btn ghost small';button.textContent='Avisos del alumno';
        button.onclick=()=>el('fjzNoticeCenter')?.click();
        (hero.querySelector('.fjz-section-tools')||hero).append(button);
      }
      return;
    }
""")
    # The read-only private inbox uses RLS plus the selected athlete filter.
    replace("if(!athlete || (!coach && currentProfile?.role!=='student'))",
            "if(!athlete || !['coach','student'].includes(currentProfile?.role))")
    replace("if(coach)return;\n     if(!('PushManager'", "if(currentProfile?.role!=='student')return;\n     if(!('PushManager'")
    signature = "async function loadStudentAlertsV96(force=false){"
    replace(signature, "let alertOwnerV96=null;\n  "+signature+"""
    const owner=currentUser?.id;
    if(owner!==alertOwnerV96){studentAlertsV96=[];studentAlertsLoadedAtV96=0;alertOwnerV96=owner}
""")
    replace("studentAlertsV96=data||[];", "if(owner!==currentUser?.id || owner!==alertOwnerV96 || mode!=='student')return [];studentAlertsV96=data||[];")
    plans = [
        ("Principiante · Cuerpo completo 2 días", [
            ("Cuerpo completo A", ["leg_press","chest_press","pulldown","leg_curl","plank"]),
            ("Cuerpo completo B", ["squat","row","incline_db","leg_ext","dead_bug"])]),
        ("Hipertrofia · Torso, pierna y cuerpo completo 3 días", [
            ("Torso", ["bench","pulldown","chest_row","lat_raise","curl"]),
            ("Pierna", ["squat","rdl","leg_curl","leg_ext","plank"]),
            ("Cuerpo completo", ["leg_press","incline_db","row","leg_curl","pushdown"])]),
        ("Hipertrofia · Empuje, tirón y piernas 3 días", [
            ("Empuje", ["bench","incline_db","lat_raise","pushdown"]),
            ("Tirón", ["pulldown","row","rear_delt","curl"]),
            ("Piernas y abdomen", ["squat","rdl","leg_press","leg_curl","floor_crunch"])]),
        ("Hipertrofia · Torso/pierna con accesorios 5 días", [
            ("Torso A", ["bench","pulldown","row","lat_raise"]),
            ("Pierna A", ["squat","leg_curl","leg_ext","dead_bug"]),
            ("Torso B", ["incline_db","chest_row","pulldown","rear_delt"]),
            ("Pierna B", ["rdl","leg_press","leg_curl","plank"]),
            ("Brazos y hombros", ["lat_raise","curl","pushdown","rear_delt"])])]
    rows = [dict(name=name, days=[dict(name=n,muscles=n,exercises=ids) for n,ids in days]) for name,days in plans]
    signature = "function showTemplates(){"
    replace(signature, signature+"for(const plan of "+json.dumps(rows,ensure_ascii=False)+"){if(!state.templates.some(t=>t.name===plan.name))state.templates.push(plan)}")
    return html
