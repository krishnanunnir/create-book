"""Cleans an EPUB in place so it reads well on Kindle.

  - Images Kindle cannot show (AVIF, WebP, wrong extension/media type) become PNG.
  - Transparent PNGs are flattened onto white (they turn black in dark mode), and
    animated GIFs become a still PNG of their first frame.
  - "Source: file:///..." lines (percollate on local pages) are removed.
  - Optional: strip title suffixes ("| Site"), delete web clutter by regex, set cover.
  - If some chapter titles start with "Part ", the TOC is nested under those parts.

Usage: python3 fix-epub.py book.epub [--cover cover.jpg]
           [--strip-suffix " | Site"]... [--junk REGEX]...
"""
import argparse, html, os, re, shutil, tempfile, zipfile
from _tools import convert, flatten, has_alpha, is_animated

ap = argparse.ArgumentParser()
ap.add_argument("epub")
ap.add_argument("--cover")
ap.add_argument("--strip-suffix", action="append", default=[])
ap.add_argument("--junk", action="append", default=[], help="regex of HTML to delete (DOTALL)")
a = ap.parse_args()

tmp = tempfile.mkdtemp()
zipfile.ZipFile(a.epub).extractall(tmp)
opf_rel = re.search(r'full-path="([^"]+)"', open(os.path.join(tmp, "META-INF/container.xml"), encoding="utf-8").read()).group(1)
oe = os.path.join(tmp, os.path.dirname(opf_rel))
opf_name = os.path.basename(opf_rel)
P = lambda f: os.path.join(oe, f)
read = lambda f: open(P(f), encoding="utf-8").read()
write = lambda f, t: open(P(f), "w", encoding="utf-8").write(t)
text_files = [os.path.relpath(os.path.join(r, f), oe) for r, _, fs in os.walk(oe) for f in fs
              if f.endswith((".xhtml", ".html", ".ncx", ".opf"))]

# 1. Kindle-safe images.
renames, dropped, flattened = {}, set(), 0
conv = os.path.join(tmp, "converted.png")  # never convert onto the source file
for r, _, fs in os.walk(oe):
    for f in fs:
        if not f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".image")):
            continue
        full = os.path.join(r, f)
        head = open(full, "rb").read(16)
        png, jpg, gif = head.startswith(b"\x89PNG"), head.startswith(b"\xff\xd8"), head.startswith(b"GIF8")
        ext = os.path.splitext(f)[1].lower()
        animated = gif and is_animated(full)
        if png and has_alpha(full) and flatten(full, conv):
            os.replace(conv, full)
            flattened += 1
        if not animated and ((png and ext == ".png") or (jpg and ext in (".jpg", ".jpeg")) or (gif and ext == ".gif")):
            continue
        new = os.path.splitext(f)[0] + (".jpg" if jpg else ".gif" if gif and not animated else ".png")
        if (png or jpg or gif) and not animated:
            os.rename(full, os.path.join(r, new))
        else:
            ok = convert(full, conv, "png")
            os.remove(full)
            if not ok:  # not a readable image (SVG, HTML error page...): drop it
                dropped.add(f)
                continue
            os.replace(conv, os.path.join(r, new))
        if new != f:
            renames[f] = new

MT = {".png": "image/png", ".jpg": "image/jpeg", ".gif": "image/gif"}
for f in text_files:
    t = read(f)
    for old, new in renames.items():
        t = t.replace(old, new)
    if f.endswith(".opf"):
        def fix_item(m):
            item = m.group(0)
            h = re.search(r'href="([^"]+)"', item)
            ext = os.path.splitext(h.group(1))[1].lower() if h else ""
            if ext in MT:
                item = re.sub(r'media-type="[^"]*"', 'media-type="%s"' % MT[ext], item)
            return item
        t = re.sub(r"<item\b[^>]*>", fix_item, t)
        t = re.sub(r"<item\b[^>]*>", lambda m: "" if any(
            ('/' + d + '"') in m.group(0) or ('"' + d + '"') in m.group(0) for d in dropped) else m.group(0), t)
    for s in a.strip_suffix:
        t = t.replace(html.escape(s, quote=False) + "<", "<").replace(s + "<", "<")
    if f.endswith((".xhtml", ".html")):
        t = re.sub(r'\s*<p class="article__url">\s*Source:\s*<a[^>]*href="file:[^"]*".*?</p>', "", t, flags=re.S)
        for j in a.junk:
            t = re.sub(j, "", t, flags=re.S)
        # Images the fetcher could not download show as broken boxes on Kindle: drop them.
        here = os.path.dirname(P(f))
        def keep_img(m):
            s = re.search(r'src="([^"]*)"', m.group(0))
            ok = s and os.path.exists(os.path.normpath(os.path.join(here, html.unescape(s.group(1)).split("?")[0])))
            return m.group(0) if ok else ""
        t = re.sub(r"<img\b[^>]*>", keep_img, t)
    write(f, t)

# 2. Nest a flat TOC (one entry per file, as percollate makes) under "Part ..." entries.
opf = read(opf_name)
items = {m.group(1): m.group(2) for m in re.finditer(r'<item\b[^>]*?id="([^"]+)"[^>]*?href="([^"]+)"', opf)}
items.update({m.group(2): m.group(1) for m in re.finditer(r'<item\b[^>]*?href="([^"]+)"[^>]*?id="([^"]+)"', opf)})
spine = [items[i] for i in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf) if i in items]
entries = []
for f in spine:
    m = re.search(r"<title>(.*?)</title>", read(f), re.S)
    if m and m.group(1).strip():
        entries.append((f, html.unescape(m.group(1).strip())))
ncx_name = next((f for f in text_files if f.endswith(".ncx")), None)
nav_name = next((f for f in text_files if 'epub:type="toc"' in read(f)), None)
if any(t.startswith("Part ") for _, t in entries) and ncx_name \
        and 'name="dtb:depth" content="1"' in read(ncx_name):  # flat TOC only
    tree, seen_part = [], False
    for e in entries:
        if e[1].startswith("Part "):
            seen_part = True
            tree.append((e, []))
        elif seen_part:
            tree[-1][1].append(e)
        else:
            tree.append((e, []))
    esc, n = html.escape, [0]
    def ncx_point(e, kids):
        n[0] += 1
        me = n[0]
        inner = "".join(ncx_point(k, []) for k in kids)
        return ('<navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
                '<content src="%s"/>%s</navPoint>\n') % (me, me, esc(e[1]), e[0], inner)
    ncx = read(ncx_name)
    ncx = re.sub(r"<navMap>.*</navMap>", lambda m: "<navMap>\n" + "".join(ncx_point(e, k) for e, k in tree) + "</navMap>", ncx, flags=re.S)
    write(ncx_name, ncx.replace('name="dtb:depth" content="1"', 'name="dtb:depth" content="2"'))
    if nav_name:
        def li(e, kids):
            sub = "<ol>" + "".join(li(k, []) for k in kids) + "</ol>" if kids else ""
            return '<li><a href="%s">%s</a>%s</li>\n' % (e[0], esc(e[1]), sub)
        nav = read(nav_name)
        nav = re.sub(r'(<nav[^>]*epub:type="toc"[^>]*>).*?(</nav>)', lambda m: m.group(1) + "<ol>\n" + "".join(li(e, k) for e, k in tree) + "</ol>" + m.group(2), nav, flags=re.S)
        write(nav_name, nav)

# 3. Cover: overwrite the image the OPF already marks as cover.
if a.cover:
    m = re.search(r'<meta name="cover" content="([^"]+)"', opf)
    href = items.get(m.group(1)) if m else None
    if not href:  # EPUB 3 marks the cover with a property instead
        m = re.search(r'<item\b[^>]*properties="[^"]*cover-image[^>]*>', opf)
        m = m and re.search(r'href="([^"]+)"', m.group(0))
        href = m.group(1) if m else None
    if href:
        fmt = "png" if href.lower().endswith(".png") else "jpeg"
        if not convert(a.cover, P(href), fmt):
            raise SystemExit("could not convert the cover image: " + a.cover)
    else:
        print("no cover slot in OPF; for Calibre builds pass --cover to ebook-convert instead")

# Rezip: mimetype first and uncompressed, as the EPUB spec requires.
out = a.epub + ".tmp"
with zipfile.ZipFile(out, "w") as z:
    z.write(os.path.join(tmp, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for r, _, fs in os.walk(tmp):
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), tmp)
            if rel != "mimetype":
                z.write(os.path.join(r, f), rel, compress_type=zipfile.ZIP_DEFLATED)
os.replace(out, a.epub)
shutil.rmtree(tmp)
print("fixed: %d images converted/renamed, %d flattened onto white" % (len(renames), flattened))
