import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    for marker in ('id="'+script_id+'"',"id='"+script_id+"'"):
        mid=html.find(marker)
        if mid>=0:
            a=html.find(">",mid); b=html.find("</script>",a)
            if a>=0 and b>=0:return html[a+1:b]
    return ""

v331=script_body("v331ProfessionalAlertGroupingRuntime")
row_start=v331.find("function rowHtml")
row_end=v331.find("const alertGroupsOpenV333",row_start)
row_block=v331[row_start:row_end] if row_start>=0 and row_end>row_start else ""
group_start=v331.find("function groupHtml")
group_end=v331.find("window.__fjzOpenGroupedAlertV331",group_start)
group_block=v331[group_start:group_end] if group_start>=0 and group_end>group_start else ""

metrics={
  "styles":len(re.findall(r"<style\b",html,re.I)),
  "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
  "channels":len(re.findall(r"\.channel\s*\(",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "intervals":len(re.findall(r"setInterval\s*\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
  "listeners":len(re.findall(r"addEventListener\s*\(",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
  "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}

checks={
  "release":tuple(map(int,release.split("."))) >= (21,38),
  "meta":'meta name="fjz-athlete-alert-curtain" content="21.38"' in html,
  "athlete_first_preserved":"reviewCenterAthleteFirstV334:true" in v331 and "alertsGroupedByAthlete:true" in v331,
  "curtain_collapsed":"alertsCollapsedByDefaultV333:true" in v331 and "__fjzToggleAlertGroupV333" in v331,
  "all_rows_inside_curtain":"athleteCurtainShowsAllRowsV338:true" in v331 and "g.rows.map(x=>rowHtml(x,{dismiss})).join('')" in group_block,
  "bulk_ok_or_superseded":(("✓ OK todas" in group_block and "__fjzResolveAthleteAlertGroupV338(this)" in group_block) or ("bulkOkUiRemovedV339:true" in v331 and "individualOkRestoredV339:true" in v331)),
  "ack_mode_valid":(("__fjzResolveGroupedAlertV336" not in row_block and "data-v336-ok-key" not in row_block) or ("individualOkRestoredV339:true" in v331 and "data-v336-ok-key" in row_block)),
  "bulk_cloud_upsert":"athleteCurtainBulkOkV338:true" in v331 and ".upsert(rows,{onConflict:'coach_id,event_key'})" in v331,
  "bulk_cloud_readback":"athleteCurtainBulkCloudReadbackV338:true" in v331 and "confirmAthleteAlertGroupAckV338" in v331 and ".in('event_key',clean)" in v331,
  "all_keys_must_confirm":"Supabase no confirmó todas las alertas del alumno." in v331,
  "one_refresh_after_bulk":"oneRefreshAfterAthleteAckV338:true" in v331 and "hydrateCoachDashboardV80" in v331,
  "open_state_cleaned":"__fjzAlertGroupsOpenV333?.delete?.(groupKey)" in v331,
  "legacy_individual_authority_preserved":"groupedAlertCloudReadbackV336:true" in v331 and "__fjzResolveGroupedAlertV336" in v331,
  "progress_copy_preserved":"coachNeverSeesKgRepAsLoadV337:true" in v331,
  "first_review_disabled":"firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
  "save_integrity":"globalSaveIntegrity:true" in html and "successDeferredUntilVerified:true" in html,
  "session_integrity":"sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
}

hard_limits={
  "styles":metrics["styles"]==1,
  "renders":metrics["renders"]<=18,
  "channels":metrics["channels"]<=2,
  "intervals":metrics["intervals"]==0,
  "listeners":metrics["listeners"]<=52,
  "mutation_observers":metrics["mutation_observers"]<=3,
  "performance_observers":metrics["performance_observers"]==0,
}

failed_checks=[k for k,v in checks.items() if not v]
failed_limits=[k for k,v in hard_limits.items() if not v]

print("TEAM FJZ V21.38 ATHLETE ALERT CURTAIN AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.38 ATHLETE ALERT CURTAIN AUDIT FAILED")
print("TEAM FJZ V21.38 ATHLETE ALERT CURTAIN AUDIT OK")
