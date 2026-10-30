import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

style_match=re.search(r"<style[^>]*>(.*?)</style>",html,re.S|re.I)
css=style_match.group(1) if style_match else ""

checks={
 "release":tuple(map(int,release.split("."))) >= (21,32),
 "meta":'meta name="fjz-nutrition-mobile-macro-geometry" content="21.32"' in html,
 "single_stylesheet":html.lower().count("<style")==1,
 "macro_nowrap":"white-space:nowrap!important" in css and ".option-head .macro-chip" in css,
 "macro_wordbreak_normal":"word-break:normal!important" in css and "overflow-wrap:normal!important" in css,
 "coach_option_stacks_mobile":"#coachStudentBody .option-head" in css and "grid-template-columns:minmax(0,1fr)!important" in css,
 "student_option_stacks_mobile":"#studentSubBody .option-head" in css,
 "actions_wrap":"#coachStudentBody .option-head>.nutrition-builder-actions" in css and "flex-wrap:wrap!important" in css,
 "narrow_phone_actions":"@media(max-width:390px)" in css and "flex:1 1 calc(50% - 7px)" in css,
 "nutrition_renderers_preserved":"renderNutritionOptionCoach" in html and "renderNutritionMealStudent" in html,
 "save_intact":"globalSaveIntegrity:true" in html and "successDeferredUntilVerified:true" in html,
 "session_guard_intact":"sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
 "review_policy_intact":"firstReviewCardsDisabledV327:true" in html,
 "comments_intact":"trainingCommentsCenterV325:true" in html,
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
print("TEAM FJZ V21.32 NUTRITION MOBILE MACRO GEOMETRY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.32 NUTRITION MOBILE MACRO GEOMETRY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.32 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.32 render regression")
if metrics["channels"]>2: raise SystemExit("V21.32 channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.32 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.32 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.32 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.32 PerformanceObserver regression")
print("TEAM FJZ V21.32 NUTRITION MOBILE MACRO GEOMETRY AUDIT OK")
