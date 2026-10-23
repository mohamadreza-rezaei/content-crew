#!/usr/bin/env python3
"""N-slide (2-10) carousel renderer: AI art background + HTML/CSS text overlay, screenshotted by headless Chrome.
Usage: render.py config.json outdir
config: {theme?: violet|emerald|sunset (palette), prefix, name, type_label, stars | badge (badge text replaces the stars chip, e.g. for official sites), brand?:"Acme", series?:"Tool of the day", font_dir?:"fonts", slides:[...]}
slide layouts:
  {"layout":"hero","art":path,"hook":..,"sub":..}                       -> big gradient tool name + hook (use for slide 1)
  {"layout":"card","art":path,"title":..,"text"?:..,"bullets"?:[..]}    -> glass card at top with title + text/bullets
  {"layout":"cta","art":path,"title":..,"text":..,"url":..,"cta":..}    -> final slide with URL + CTA button
Footer always shows page indicator 'n / N →' (last slide shows brand)."""
import json,sys,os,subprocess,html
from PIL import Image
T=os.path.dirname(os.path.abspath(__file__))
c=json.load(open(sys.argv[1])); FD=os.path.abspath(c.get("font_dir",os.path.join(T,"fonts"))); out=os.path.abspath(sys.argv[2]); os.makedirs(out,exist_ok=True)
e=html.escape; FA="۰۱۲۳۴۵۶۷۸۹"
fa=lambda n:"".join(FA[int(d)] for d in str(n))
CSS=f"""
@font-face{{font-family:V;src:url(file://{FD}/Vazirmatn-Regular.woff2);font-weight:400}}
@font-face{{font-family:V;src:url(file://{FD}/Vazirmatn-Bold.woff2);font-weight:700}}
@font-face{{font-family:V;src:url(file://{FD}/Vazirmatn-ExtraBold.woff2);font-weight:800}}
@font-face{{font-family:V;src:url(file://{FD}/Vazirmatn-Black.woff2);font-weight:900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1080px;overflow:hidden;background:#07061a;font-family:V,sans-serif;color:#fff}}
.s{{position:relative;width:1080px;height:1080px;overflow:hidden}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
.shade{{position:absolute;inset:0}}
.top{{position:absolute;top:56px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center;direction:ltr}}
.brand{{font-weight:900;font-size:34px;letter-spacing:.5px;display:flex;align-items:center;gap:12px}}
.dot{{width:18px;height:18px;border-radius:6px;background:linear-gradient(135deg,#ff5f6d,#7b5cff 60%,#22d3ee);box-shadow:0 0 24px #7b5cffaa}}
.pill{{font-size:22px;font-weight:700;padding:10px 22px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);backdrop-filter:blur(14px)}}
.grad{{background:linear-gradient(90deg,#ff6a7a,#b48cff 55%,#5ee7ff);-webkit-background-clip:text;color:transparent}}
.foot{{position:absolute;bottom:52px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center;direction:ltr;font-size:24px;font-weight:700;color:rgba(255,255,255,.88)}}
.chip{{padding:12px 24px;border-radius:16px;background:rgba(10,8,30,.6);border:1px solid rgba(255,255,255,.16);backdrop-filter:blur(16px)}}
.card{{position:absolute;top:130px;left:64px;right:64px;direction:rtl;padding:30px 40px;border-radius:36px;background:linear-gradient(135deg,rgba(20,16,50,.80),rgba(20,16,50,.56));border:1px solid rgba(255,255,255,.18);backdrop-filter:blur(22px);box-shadow:0 30px 80px rgba(0,0,0,.5)}}
.kick{{font-size:22px;font-weight:800;color:#ff8a95;margin-bottom:6px}}
.ttl{{font-weight:900;font-size:46px;line-height:1.3}}
.txt{{font-size:28px;font-weight:400;line-height:1.6;margin-top:12px;color:rgba(255,255,255,.9)}}
.li{{display:flex;gap:18px;align-items:flex-start;margin-top:16px}}
.num{{flex:none;width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#ff5f6d,#7b5cff);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:24px;margin-top:2px}}
.lit{{font-size:28px;font-weight:700;line-height:1.45}}
.ltr{{direction:ltr;unicode-bidi:isolate}}
"""
THEMES={
 "violet":{},
 "emerald":{"#ff5f6d":"#34d399","#7b5cff":"#0ea5a4","#22d3ee":"#fbbf24","#ff6a7a":"#6ee7b7","#b48cff":"#5eead4","#5ee7ff":"#fcd34d","#ff8a95":"#fcd34d","#07061a":"#050f0e","7,6,26":"4,16,15","20,16,50":"8,32,30","10,8,30":"4,20,18"},
 "sunset":{"#ff5f6d":"#fb923c","#7b5cff":"#f43f5e","#22d3ee":"#facc15","#ff6a7a":"#fdba74","#b48cff":"#fb7185","#5ee7ff":"#fde047","#ff8a95":"#fdba74","#07061a":"#0a0a12","7,6,26":"10,10,20","20,16,50":"28,22,36","10,8,30":"16,14,24"},
}
TH=THEMES[c.get("theme","violet")]
def page(b):
    h=f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{b}</body></html>"
    for k,v in TH.items(): h=h.replace(k,v)
    return h
N=len(c["slides"]); brand=c.get("brand","Acme")
def top(i): return f"<div class=top><div class=brand><span class=dot></span>{brand}</div><div class=pill>{e(c['name']) if i else e(c.get('series','Tool of the day'))+' · '+e(c['type_label'])}</div></div>"
def foot(i,left):
    right=f"{i+1} / {N} →" if i<N-1 else f"{N} / {N} · {brand}"
    return f"<div class=foot>{left}<div class=chip>{right}</div></div>"
def bg(s,shade): return f"<div class=bg style=\"background-image:url(file://{os.path.abspath(s['art'])})\"></div><div class=shade style=\"background:{shade}\"></div>"
SH_HERO="linear-gradient(180deg,rgba(7,6,26,.92) 0%,rgba(7,6,26,.55) 30%,rgba(7,6,26,0) 48%,rgba(7,6,26,0) 72%,rgba(7,6,26,.85) 100%)"
SH_CARD="linear-gradient(180deg,rgba(7,6,26,.55) 0%,rgba(7,6,26,.15) 50%,rgba(7,6,26,.9) 100%)"
def body(s):
    h=""
    if s.get("kicker"): h+=f"<div class=kick>{e(s['kicker'])}</div>"
    h+=f"<div class=ttl><span class=grad>{e(s['title'])}</span></div>"
    if s.get("text"): h+=f"<div class=txt>{e(s['text'])}</div>"
    for k,b in enumerate(s.get("bullets",[])): h+=f"<div class=li><span class=num>{fa(k+1)}</span><span class=lit>{e(b)}</span></div>"
    return h
for i,s in enumerate(c["slides"]):
    L=s.get("layout","card")
    if L=="hero":
        h=f"""<div class=s>{bg(s,SH_HERO)}{top(i)}
<div style="position:absolute;top:150px;left:40px;right:40px;text-align:center">
<div class=grad style="font-weight:900;font-size:{s.get('name_size',112)}px;line-height:1.05;direction:ltr;letter-spacing:-2px">{e(c['name'])}</div>
<div style="direction:rtl;font-weight:800;font-size:44px;margin-top:14px;text-shadow:0 2px 6px #000,0 4px 30px #000">{e(s['hook'])}</div>
<div style="margin-top:14px"><span style="display:inline-block;direction:rtl;font-weight:700;font-size:26px;padding:10px 26px;border-radius:999px;background:rgba(10,8,30,.72);border:1px solid rgba(255,255,255,.16);backdrop-filter:blur(14px);color:rgba(255,255,255,.95)">{e(s['sub'])}</span></div></div>
{foot(i,f"<div class=chip>{e(c['badge']) if c.get('badge') else '★ '+e(c['stars'])+' GitHub Stars'}</div>")}</div>"""
    elif L=="cta":
        h=f"""<div class=s>{bg(s,SH_CARD)}{top(i)}<div class=card>{body(s)}</div>
{foot(i,f"<div class=chip style='direction:ltr'>{e(s['url'])}</div>")}
<div style="position:absolute;bottom:130px;left:0;right:0;display:flex;justify-content:center"><div class=chip style="direction:rtl;background:linear-gradient(90deg,#ff5f6d,#7b5cff);border:none;font-size:28px;font-weight:800;padding:16px 36px">{e(s['cta'])}</div></div></div>"""
    else:
        h=f"""<div class=s>{bg(s,SH_CARD)}{top(i)}<div class=card>{body(s)}</div>{foot(i,"<div></div>")}</div>"""
    hp=f"{out}/slide{i+1}.html"; open(hp,"w").write(page(h)); png=f"{out}/slide{i+1}.png"
    if os.path.exists(png): os.remove(png)
    subprocess.run([os.environ.get("CHROME","google-chrome"),"--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars","--allow-file-access-from-files","--force-device-scale-factor=1","--virtual-time-budget=3000","--window-size=1080,1080",f"--screenshot={png}",f"file://{hp}"],check=True,capture_output=True)
    im=Image.open(png).convert("RGB"); assert im.size==(1080,1080),im.size
    jp=f"{out}/{c.get('prefix','slide')}-slide{i+1}.jpg"; im.save(jp,"JPEG",quality=94,optimize=True); print(jp)
