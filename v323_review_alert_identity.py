import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":doc.lower().count("<style"),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    mid=-1
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=doc.find(marker)
        if mid>=0: break
    if mid<0: raise RuntimeError("V21.23 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.23 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-review-server-authority" content="21.22"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "stableClientReviewAuthorityV319:true",
    "serverFeedRequiredForReviewCardsV322:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.23 prerequisite missing "+marker)

def patch_v302(body):
    old="""  const feed=s=>{try{const a=athlete(s),f=Array.isArray(coachFeedV235)?coachFeedV235:[];return a?f.filter(x=>String(x?.athlete_id||'')===String(a.id)):[]}catch(_e){return []}};"""
    new="""  const feed=s=>{
    try{
      const f=Array.isArray(coachFeedV235)?coachFeedV235:[];
      const stableId=String(typeof athleteKeyV308==='function'
        ?athleteKeyV308(s)
        :(athlete(s)?.id||s?.id||''));
      return stableId?f.filter(x=>String(x?.athlete_id||'')===stableId):[];
    }catch(_e){return []}
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V21.23 V302 feed identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    const at=athlete(s),reviewKey=REVIEW_PREFIX+String(at?.id||s.id)+':'+sourceType+':'+hash(source);"""
    new="""    const stableAthleteIdV323=String(typeof athleteKeyV308==='function'
      ?athleteKeyV308(s)
      :(athlete(s)?.id||s.id||'unknown')),
      reviewKey=REVIEW_PREFIX+stableAthleteIdV323+':'+sourceType+':'+hash(source);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.23 review key identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    cloudAuthorityRepaintsReviewCenterV322:true,"""
    new="""    cloudAuthorityRepaintsReviewCenterV322:true,
    stableServerAlertIdentityV323:true,
    reviewFeedUsesAthleteKeyV308:true,
    reviewKeysUseStableAthleteIdV323:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.23 V302 flags anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)
html=html.replace("</head>",'<meta name="fjz-review-alert-identity" content="21.23">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.23 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-alert-identity" content="21.23"',
    "typeof athleteKeyV308==='function'",
    "stableServerAlertIdentityV323:true",
    "reviewFeedUsesAthleteKeyV308:true",
    "reviewKeysUseStableAthleteIdV323:true",
    "serverFeedRequiredForReviewCardsV322:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.23 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.23 review alert identity bridge")
print("V21.23 BEFORE:",before)
print("V21.23 AFTER:",after)
