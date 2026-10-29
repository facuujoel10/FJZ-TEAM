import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def body(sid):
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=html.find(marker)
        if mid>=0:
            a=html.find(">",mid); b=html.find("</script>",a)
            if a>=0 and b>=0:return html[a+1:b]
    return ""

v175=body("v175ProfileAgendaCoachCenterRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,30),
 "meta":'meta name="fjz-comments-pending-inbox" content="21.30"' in html,
 "dashboard_pending_only":"const visible=pendingRows.slice(0,8)" in v302 and "trainingCommentsInboxPendingOnlyV330:true" in v302,
 "dashboard_reviewed_removed":"reviewedCommentsLeaveDashboardV330:true" in v302,
 "dashboard_empty_copy":"Sin comentarios pendientes" in v302,
 "student_panel_pending_only":"pendingRows.slice(0,10)" in v175 and "reviewedCommentsLeave360PanelV330:true" in v175,
 "history_remains_source":"Los revisados siguen visibles dentro del historial de cada sesión." in v175,
 "ok_preserved":"trainingCommentOkV329:true" in v302 and "__fjzAckTrainingCommentV329" in v302,
 "save_intact":"globalSaveIntegrity:true" in v304 and "successDeferredUntilVerified:true" in v304,
 "session_guard_intact":"sessionSuccessRequiresDoubleVerification:true" in v316 and "snapshotAndProjectionConfirmation:true" in v316,
}
failed=[k for k,v in checks.items() if not v]
metrics={
 "styles":html.lower().count("<style"),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":html.count(".channel("),
 "timeouts":html.count("setTimeout("),
 "intervals":html.count("setInterval("),
 "listeners":html.count("addEventListener("),
 "mutation_observers":html.count("new MutationObserver"),
 "performance_observers":html.count("new PerformanceObserver"),
}
print("TEAM FJZ V21.30 COMMENTS INBOX AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.30 COMMENTS INBOX AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.30 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.30 render regression")
if metrics["channels"]>2: raise SystemExit("V21.30 channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.30 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.30 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.30 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.30 PerformanceObserver regression")
print("TEAM FJZ V21.30 COMMENTS INBOX AUDIT OK")
