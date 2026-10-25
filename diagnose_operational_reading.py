import pathlib,re,json
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
terms=["Preparando lectura operativa","lectura operativa","Preparando lectura","requiere revisión","Requiere revisión","Primer chequeo","Preparando"]
print("TEAM FJZ DIAGNOSTIC OPERATIONAL READING")
for term in terms:
    hits=[m.start() for m in re.finditer(re.escape(term),html,re.I)]
    print("TERM",repr(term),"COUNT",len(hits))
    for i,pos in enumerate(hits[:25],1):
        s=max(0,pos-700);e=min(len(html),pos+1600)
        ctx=html[s:e].replace("\\n"," ")
        # nearest script id before the hit
        before=html[:pos]
        sm=list(re.finditer(r'<script[^>]*\\bid=["\\\']([^"\\\']+)["\\\']',before,re.I))
        sid=sm[-1].group(1) if sm else "NO_SCRIPT"
        print("HIT",i,"POS",pos,"SCRIPT",sid)
        print(ctx)
print("TEAM FJZ DIAGNOSTIC END")
