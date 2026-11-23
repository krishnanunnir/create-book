"""Screenshots one page of an EPUB at phone width, to check it by eye.
Usage: python3 preview-epub.py book.epub [N] [--scroll PX] [--scale 2] [--out shot.png]

N is the page number check-epub.py prints (default 1). The shot is 360x1300 CSS
pixels; --scroll moves that window down the chapter. --scale 2 gives a sharper
image, for checking that diagram borders line up.
"""
import argparse, os, re, shutil, tempfile, urllib.parse, zipfile
from _tools import screenshot

ap = argparse.ArgumentParser()
ap.add_argument("epub")
ap.add_argument("page", nargs="?", type=int, default=1)
ap.add_argument("--scroll", type=int, default=0)
ap.add_argument("--scale", type=int, default=1)
ap.add_argument("--out", default="shot.png")
a = ap.parse_args()

tmp = tempfile.mkdtemp()
try:
    zipfile.ZipFile(a.epub).extractall(tmp)
    container = open(os.path.join(tmp, "META-INF/container.xml"), encoding="utf-8").read()
    opf_rel = re.search(r'full-path="([^"]+)"', container).group(1)
    opf = open(os.path.join(tmp, opf_rel), encoding="utf-8").read()
    hrefs = {}
    for m in re.finditer(r"<item\b[^>]*>", opf):
        i = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(0)))
        hrefs[i.get("id")] = i.get("href")
    spine = [hrefs[i] for i in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf) if i in hrefs]
    if not 1 <= a.page <= len(spine):
        raise SystemExit(f"page must be 1..{len(spine)}")
    chapter = os.path.join(os.path.dirname(opf_rel), urllib.parse.unquote(spine[a.page - 1]))
    # A headless window on its own lays out too wide, so the chapter goes in a 360px iframe.
    view = os.path.join(tmp, "_view.html")
    open(view, "w", encoding="utf-8").write(
        "<html><body style='margin:0;overflow:hidden;background:#fff'>"
        f"<iframe src='{urllib.parse.quote(chapter)}' style='border:0;width:360px;"
        f"height:{a.scroll + 1300}px;margin-top:-{a.scroll}px'></iframe></body></html>")
    screenshot(view, os.path.abspath(a.out), 360, 1300, scale=a.scale, wait_ms=5000)
    print(f"page {a.page} ({spine[a.page - 1]}) at {a.scroll}px -> {a.out}")
finally:
    shutil.rmtree(tmp)
