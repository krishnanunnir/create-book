"""Checks an EPUB for the problems that make Kindle books look bad.
Usage: python3 check-epub.py book.epub [--width 52]
Reports: tiny pages (blank-page bug), code/diagram lines wider than a phone,
images Kindle cannot show, broken references, local file paths, invalid XML,
the TOC, and the cover size. Exit code 1 if anything is a hard problem.
"""
import argparse, html, os, re, subprocess, sys, tempfile, zipfile
ap = argparse.ArgumentParser(); ap.add_argument("epub"); ap.add_argument("--width", type=int, default=52)
a = ap.parse_args()
tmp = tempfile.mkdtemp(); zipfile.ZipFile(a.epub).extractall(tmp)
z = zipfile.ZipFile(a.epub); hard = []
if z.namelist()[0] != "mimetype": hard.append("mimetype is not the first zip entry")
opf_rel = re.search(r'full-path="([^"]+)"', open(os.path.join(tmp, "META-INF/container.xml")).read()).group(1)
oe = os.path.join(tmp, os.path.dirname(opf_rel)); opf = open(os.path.join(tmp, opf_rel)).read()
items = {}
for m in re.finditer(r"<item\b[^>]*>", opf):
    i = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(0))); items[i.get("id")] = i
spine = [items[i]["href"] for i in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf) if i in items]

print("== Pages (spine order)")
for f in spine:
    t = open(os.path.join(oe, f), encoding="utf-8").read()
    words = len(html.unescape(re.sub(r"<[^>]+>", " ", t[t.find("<body"):])).split())
    imgs = len(re.findall(r"<img|<image", t))
    flag = "  <-- near-empty page?" if words < 60 and not imgs else ""
    title = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    print(f"  {words:6} words {imgs:3} img  {re.sub('<[^>]+>','',title.group(1)).strip()[:60] if title else f}{flag}")

print(f"== Code/diagram lines over {a.width} chars (wrap on phones)")
wide = 0
for f in spine:
    for p in re.findall(r"<pre.*?</pre>", open(os.path.join(oe, f), encoding="utf-8").read(), re.S):
        for l in html.unescape(re.sub(r"<[^>]+>", "", p)).splitlines():
            if len(l) > a.width:
                wide += 1
                if wide <= 15: print(f"  {len(l):3} {f[:30]}: {l[:70]}")
print(f"  total: {wide}")

print("== Images")
for i in items.values():
    h = i.get("href", ""); mt = i.get("media-type", "")
    if mt.startswith("image") or h.lower().endswith((".webp", ".avif", ".image")):
        head = open(os.path.join(oe, h), "rb").read(16) if os.path.exists(os.path.join(oe, h)) else b""
        real = "png" if head.startswith(b"\x89PNG") else "jpeg" if head.startswith(b"\xff\xd8") else "gif" if head.startswith(b"GIF8") else "svg+xml" if b"<" in head else "OTHER"
        if mt != f"image/{real}": hard.append(f"image {h}: media-type {mt!r}, content is {real} (run fix-epub.py)")

print("== References and leaks")
for r, _, fs in os.walk(oe):
    for f in fs:
        if f.endswith((".xhtml", ".html")):
            t = open(os.path.join(r, f), encoding="utf-8").read()
            for attr, s in re.findall(r'(?<![\w-])(src|href)="(?!https?:|mailto:|#|data:)([^"#]+)', t):
                if not os.path.exists(os.path.normpath(os.path.join(r, html.unescape(s).split("?")[0]))):
                    if attr == "src": hard.append(f"{f}: missing image {s[:80]}")
                    else: print(f"  note: dead relative link in {f}: {s[:80]}")
            if "file:///" in t: hard.append(f"{f}: contains a local file:/// path")
            x = subprocess.run(["xmllint", "--noout", os.path.join(r, f)], capture_output=True, text=True)
            if x.returncode: hard.append(f"{f}: invalid XML: {x.stderr.splitlines()[0][:100]}")

print("== TOC")
ncx = next((os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.endswith(".ncx")), None)
if ncx:
    t = open(ncx).read(); depth = 0
    for tok in re.finditer(r"<navPoint\b|</navPoint>|<text>(.*?)</text>", t):
        if tok.group(0).startswith("<navPoint"): depth += 1
        elif tok.group(0) == "</navPoint>": depth -= 1
        elif depth: print("  " + "  " * depth + html.unescape(tok.group(1))[:70])
    orders = re.findall(r'playOrder="(\d+)"', t)
    if len(orders) != len(set(orders)): hard.append("duplicate playOrder values in toc.ncx")

print("== Cover")
m = re.search(r'<meta name="cover" content="([^"]+)"', opf)
c = items.get(m.group(1), {}).get("href") if m else None
if c:
    s = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", os.path.join(oe, c)], capture_output=True, text=True).stdout
    w, h = re.findall(r"pixel\w+: (\d+)", s)
    print(f"  {c}: {w}x{h}" + ("" if int(h) >= 2500 else "  (Kindle recommends 1600x2560)"))
else:
    print("  no cover")

print("== Result")
for h in hard: print("  PROBLEM:", h)
print("  OK" if not hard else f"  {len(hard)} problem(s)")
sys.exit(1 if hard else 0)
