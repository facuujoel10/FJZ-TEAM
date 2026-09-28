import pathlib,re
from html.parser import HTMLParser
from collections import Counter

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v143InteractionQAStyles">
/* Interaction guards: hidden overlays can never intercept pointer input. */
.hidden,[hidden]{pointer-events:none!important}
.modal-wrap{pointer-events:none}
.modal-wrap[style*="display: flex"],.modal-wrap[style*="display:flex"]{pointer-events:auto}
.auth-gate{pointer-events:none}
.auth-gate[style*="display: flex"],.auth-gate[style*="display:flex"]{pointer-events:auto}
button:disabled{cursor:not-allowed;opacity:.58}
button,.btn,.tab,input,select,textarea{touch-action:manipulation}
input,select,textarea{pointer-events:auto}
</style>
"""

js=r"""
<script id="v143InteractionQARuntime">
(function(){
  const QA={
    version:'14.3',
    errors:0,
    rejections:0,
    lastError:null,
    lastRejection:null,
    startedAt:new Date().toISOString()
  };

  window.addEventListener('error',ev=>{
    QA.errors++;
    QA.lastError=String(ev?.message||'Error');
  });

  window.addEventListener('unhandledrejection',ev=>{
    QA.rejections++;
    QA.lastRejection=String(ev?.reason?.message||ev?.reason||'Promise rejection');
  });

  // Escape closes only an actually visible modal. It does not change app state.
  document.addEventListener('keydown',ev=>{
    if(ev.key!=='Escape')return;
    const wrap=el('modalWrap');
    if(wrap&&getComputedStyle(wrap).display!=='none'){
      closeModal();
    }
  });

  window.__fjzInteractionQA=QA;
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# ---------- Static interaction audit ----------
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.handlers=[]
        self.buttons=0
        self.inputs=0
        self.selects=0
        self.textareas=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'): self.ids.append(d['id'])
        if tag=='button': self.buttons+=1
        elif tag=='input': self.inputs+=1
        elif tag=='select': self.selects+=1
        elif tag=='textarea': self.textareas+=1
        for k,v in attrs:
            if k in ('onclick','onchange','oninput','onblur','onfocus','onsubmit') and v:
                self.handlers.append((k,v))

parser=Parser()
parser.feed(html)

id_counts=Counter(parser.ids)
dupes={k:v for k,v in id_counts.items() if v>1}

# Extract direct handler function calls. Ignore JS built-ins and methods.
called=set()
for _,code in parser.handlers:
    for name in re.findall(r'(?<![\.\w$])([A-Za-z_$][\w$]*)\s*\(',code):
        if name not in {'if','for','while','switch','Number','String','Date','Math','parseInt','parseFloat','setTimeout'}:
            called.add(name)

def defined(name):
    patterns=[
        rf'function\s+{re.escape(name)}\s*\(',
        rf'\b{name}\s*=\s*(?:async\s*)?function\s*\(',
        rf'\b{name}\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
        rf'window\.{re.escape(name)}\s*=',
        rf'Object\.assign\(window,\{{[^}}]*\b{re.escape(name)}\b'
    ]
    return any(re.search(pat,html,re.S) for pat in patterns)

undefined=sorted(name for name in called if not defined(name))

# Critical interaction functions must always exist in a releasable build.
critical=[
    'render','showModal','closeModal','showAuthGate','loginCloud','logoutCloud',
    'openStudent','switchNutritionViewV70','startWorkout','finishWorkout',
    'submitWeeklyCheckin','submitMeasurement'
]
missing_critical=[x for x in critical if not defined(x)]
if missing_critical:
    raise RuntimeError("V14.3 missing critical interaction handlers: "+repr(missing_critical))

# Some handler names may be deliberately imported/lexical in generated code.
# We report all unresolved names, but only fail for critical handlers above.
if re.search(r'(?:html|body)\s*\{[^}]*overflow-y\s*:\s*hidden',html,re.I|re.S):
    raise RuntimeError("V14.3 root vertical scroll is hidden")
if re.search(r'addEventListener\s*\(\s*[\'"]wheel[\'"].*?preventDefault\s*\(',html,re.I|re.S):
    raise RuntimeError("V14.3 wheel preventDefault detected")
if re.search(r'addEventListener\s*\(\s*[\'"]touchmove[\'"].*?preventDefault\s*\(',html,re.I|re.S):
    raise RuntimeError("V14.3 touchmove preventDefault detected")

critical_ids=['modalWrap','modal','authGate','authCard','app','view']
missing_ids=[x for x in critical_ids if x not in id_counts]
if missing_ids:
    raise RuntimeError("V14.3 missing critical DOM ids: "+repr(missing_ids))

critical_dupes={k:v for k,v in dupes.items() if k in critical_ids}
if critical_dupes:
    raise RuntimeError("V14.3 duplicated critical DOM ids: "+repr(critical_dupes))

metrics={
    'buttons':parser.buttons,
    'inputs':parser.inputs,
    'selects':parser.selects,
    'textareas':parser.textareas,
    'inline_handlers':len(parser.handlers),
    'unique_handler_calls':len(called),
    'unresolved_handler_names':undefined,
    'duplicate_ids':dupes,
    'wheel_listeners':len(re.findall(r'addEventListener\s*\(\s*[\'"]wheel[\'"]',html,re.I)),
    'touchmove_listeners':len(re.findall(r'addEventListener\s*\(\s*[\'"]touchmove[\'"]',html,re.I)),
    'prevent_defaults':html.count('preventDefault('),
    'modal_wrap_present':bool(id_counts.get('modalWrap')),
    'auth_gate_present':bool(id_counts.get('authGate')),
}

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.3 INTERACTION QA:",metrics)
