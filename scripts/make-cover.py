"""Renders a 1600x2560 book cover (Kindle's recommended size) from a JSON spec.
Usage: python3 make-cover.py spec.json out.jpg

spec.json keys (all strings unless noted):
  accent   "#f5a524"            accent color
  kicker   "A HANDS-ON GUIDE"   small caps line above the title
  title    "Temporal<br>in Practice"   use <br> for line breaks
  sub      one-sentence promise under the title
  events   [["2021", "Snap  what they wrote"], ...]  up to ~8 timeline rows;
           "Name  rest" (two spaces) bolds Name; text starting "!!" shows in red
  foot     short line at the bottom
"""
import json, os, subprocess, sys, tempfile
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

def label(t):  # "Company  what" -> bold company name
    t = t.removeprefix("!!")  # "!!" only marks the row red (see page())
    who, sep, what = t.partition("  ")
    return f"<b>{who}</b>&nbsp;&nbsp;{what}" if sep else t

def page(b):
    rows = "".join(
        f'<div class="ev{" bad" if t.startswith("!!") else ""}"><span class="dot"></span>'
        f'<span class="n">{n}</span><span class="t">{label(t)}</span></div>' for n, t in b["events"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1600px;height:2560px;overflow:hidden}}
body{{background:#0b1020;color:#f2f4f8;font-family:'Avenir Next','Helvetica Neue',sans-serif;position:relative}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 2px,transparent 2px),linear-gradient(90deg,#ffffff08 2px,transparent 2px);background-size:80px 80px}}
.glow{{position:absolute;width:1500px;height:1500px;right:-600px;top:-500px;border-radius:50%;background:radial-gradient({b['accent']}33,transparent 65%)}}
.wrap{{position:absolute;inset:150px 140px}}
.kicker{{font-size:44px;letter-spacing:12px;font-weight:600;color:{b['accent']}}}
.bar{{width:160px;height:12px;background:{b['accent']};margin:44px 0 60px}}
h1{{font-family:Georgia,serif;font-weight:700;font-size:200px;line-height:1.02;margin:0;letter-spacing:-3px}}
.sub{{font-size:58px;line-height:1.35;color:#c9d1e3;margin-top:70px;max-width:1250px}}
.hist{{position:absolute;left:0;right:0;bottom:330px;font-family:Menlo,monospace;font-size:40px;color:#9aa6c4}}
.hist:before{{content:'';position:absolute;left:15px;top:30px;bottom:30px;width:4px;background:#ffffff22}}
.ev{{display:flex;align-items:center;height:78px;position:relative}}
.dot{{width:34px;height:34px;border-radius:50%;background:#0b1020;border:6px solid {b['accent']};box-sizing:border-box;flex:none}}
.ev.bad .dot{{border-color:#f87171}} .ev.bad{{color:#f87171}}
.n{{width:150px;text-align:right;margin-right:44px;color:{b['accent']};font-weight:700}}
.foot{{position:absolute;left:0;right:0;bottom:0;border-top:4px solid #ffffff22;padding-top:56px;font-size:46px;color:#c9d1e3;display:flex;justify-content:space-between}}
b{{color:#e6eaf3;font-weight:700}}
.foot b{{color:{b['accent']};font-weight:600}}
</style></head><body><div class="grid"></div><div class="glow"></div><div class="wrap">
<div class="kicker">{b['kicker']}</div><div class="bar"></div><h1>{b['title']}</h1>
<div class="sub">{b['sub']}</div><div class="hist">{rows}</div>
<div class="foot"><span>{b['foot']}</span></div></div></body></html>"""


b = json.load(open(sys.argv[1])); out = os.path.abspath(sys.argv[2])
d = tempfile.mkdtemp(); h = os.path.join(d, "c.html"); png = os.path.join(d, "c.png")
open(h, "w").write(page(b))
subprocess.run([BRAVE, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1600,2560",
                f"--screenshot={png}", "file://" + h], check=True, capture_output=True)
subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90", png, "--out", out],
               check=True, capture_output=True)
print("cover:", out)
