import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.21 LEGACY PROFILE RENDER CONSOLIDATION
# =========================================================
# V11.9 still carries one post-render cleanup wrapper after V12.5:
#   fjzPostRenderV125('profile-guard-v119', removeLegacyProfileV119)
#
# V14 already exports the same function and invokes it from finalPass():
#   window.__fjzRemoveLegacyProfileV119?.()
#
# Remove only the duplicate V11.9 render wrapper. Preserve:
# - initial profile cleanup
# - legacy-profile CSS hard hide
# - PWA/service-worker refresh handling
# - V14 canonical cleanup on every render
#
# No navigation, measurement, workout, realtime or payment logic changes.

def metrics(doc):
    return {
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "v119_render_wrappers":len(re.findall(
            r"const\s+baseRenderV119\s*=\s*window\.render;[\s\S]*?window\.render\s*=\s*function\(\)",
            doc
        )),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.21 missing script: "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.21 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)
if before["render_assignments"]!=22:
    raise RuntimeError("V20.21 unexpected render baseline: "+repr(before))
if before["v119_render_wrappers"]!=1:
    raise RuntimeError("V20.21 expected one V11.9 render wrapper: "+repr(before))

if "window.__fjzRemoveLegacyProfileV119=removeLegacyProfileV119;" not in html:
    raise RuntimeError("V20.21 V14/V11.9 exported cleanup missing")
if "window.__fjzRemoveLegacyProfileV119?.();" not in html:
    raise RuntimeError("V20.21 V14 canonical cleanup call missing")

def patch_v119(body):
    start_marker="  const baseRenderV119=window.render;"
    end_marker="  document.addEventListener('DOMContentLoaded',removeLegacyProfileV119,{once:true});"

    if body.count(start_marker)!=1:
        raise RuntimeError("V20.21 V11.9 render start mismatch: "+str(body.count(start_marker)))
    if body.count(end_marker)!=1:
        raise RuntimeError("V20.21 V11.9 render end mismatch: "+str(body.count(end_marker)))

    start=body.index(start_marker)
    end=body.index(end_marker,start)
    block=body[start:end]

    required=[
        "window.render=function()",
        "baseRenderV119.apply(this,arguments)",
        "profile-guard-v119",
        "removeLegacyProfileV119",
        "return out;",
    ]
    missing=[x for x in required if x not in block]
    if missing:
        raise RuntimeError("V20.21 V11.9 wrapper shape changed: "+repr(missing))

    return body[:start]+"""  // V20.21: per-render cleanup delegated to V14 finalPass.

"""+body[end:]

html=edit_script(html,"v119LegacyProfileHardGuard",patch_v119)

after=metrics(html)
if after["render_assignments"]!=21:
    raise RuntimeError("V20.21 expected render assignments 22 -> 21: "+repr({"before":before,"after":after}))
if after["v119_render_wrappers"]!=0:
    raise RuntimeError("V20.21 legacy V11.9 render wrapper still present")

# Removing this wrapper should not change timer/RAF/listener counts.
for key in ("timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.21 must preserve "+key+": "+repr({"before":before,"after":after}))

critical=[
    "window.__fjzRemoveLegacyProfileV119=removeLegacyProfileV119;",
    "window.__fjzRemoveLegacyProfileV119?.();",
    "removeLegacyProfileV119();",
    "v119LegacyProfileHardHide",
    "__fjzProfileGuardV119",
    "controllerchange",
    "navigator.serviceWorker.getRegistration()",
    "consolidatedRuntime:true",
    "final-v140",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.21 missing profile/PWA behavior: "+repr(missing))

runtime=r"""
<script id="v221LegacyProfileRenderConsolidationRuntime">
(function(){
  window.__fjzV221={
    version:'20.21',
    legacyProfileRenderWrapperRemoved:true,
    v14CleanupAuthorityPreserved:true,
    initialCleanupPreserved:true,
    pwaRefreshPreserved:true,
    profileHardHidePreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.21 legacy profile render consolidation")
print("V20.21 BEFORE:",before)
print("V20.21 AFTER:",after)
print("V20.21 V11.9 duplicate render cleanup delegated to V14")
