"""Checks the shape of each chapter in Markdown book sources before building.
Usage: python3 lint-md.py md/*.md   (files are read in the order given)
Per chapter (# h1): words, longest stretch with no heading, long paragraphs,
stock AI phrases, "In this chapter..." openers, wide code lines. Then prints
each chapter's first and last sentence, so the hand-off from one chapter to the
next can be read in one pass. Advisory only: always exits 0.
"""
import re, statistics, sys

TELLS = r"\b(delve|tapestry|game[- ]changer|seamless(ly)?|robust|leverag(e|ing)|unlock|" \
    r"in today's|fast-paced|it's (important|worth) (to note|noting)|let's dive|" \
    r"dive (deep|into)|navigat(e|ing) the|landscape|in conclusion|at the end of the day|" \
    r"plays a (crucial|vital|key) role|not just .{1,30}, but|the key insight|" \
    r"the tricky part|(gets|get) interesting|at its core|tl;dr|the rest follows|" \
    r"it all falls out|simply)\b"
OPENER = r"^(in this chapter|this chapter (will|covers|explores)|welcome to|now that we)"

lines, prose, chapters = [], [], []
for f in sys.argv[1:]:
    lines += open(f, encoding="utf-8").read().splitlines()
fence = False
for l in lines:
    if l.startswith("```"):
        fence = not fence
        continue
    if fence:
        if len(l) > 52 and chapters: chapters[-1]["wide"] += 1
        continue
    if l.startswith("# "):
        chapters.append({"title": l[2:].strip(), "paras": [[]], "runs": [0], "wide": 0})
    elif chapters:
        c = chapters[-1]
        if re.match(r"#{2,6} ", l): c["runs"].append(0); c["paras"].append([])
        elif not l.strip() or l.startswith(("|", "![", "---")): c["paras"].append([])
        else: c["paras"][-1].append(l); c["runs"][-1] += len(l.split())

body = [c for c in chapters if sum(c["runs"]) > 0]
for c in body:
    c["words"] = sum(c["runs"])
    c["paras"] = [" ".join(p) for p in c["paras"] if p]
med = statistics.median(c["words"] for c in body) if body else 0

print(f"== Chapter shape (median {med:.0f} words)")
for c in body:
    notes = []
    if c["words"] < 400: notes.append("short: merge or grow?")
    if c["words"] > 2 * med and len(body) > 2: notes.append("over 2x median: split?")
    if max(c["runs"]) > 1200: notes.append(f"{max(c['runs'])} words with no ## heading")
    long = sum(len(p.split()) > 120 for p in c["paras"])
    if long: notes.append(f"{long} paragraph(s) over 120 words")
    tells = re.findall(TELLS, " ".join(c["paras"]), re.I)
    if tells: notes.append(f"{len(tells)} stock phrase(s): " + ", ".join(sorted({t[0].lower() for t in tells}))[:60])
    if c["paras"] and re.match(OPENER, c["paras"][0], re.I): notes.append("opens with a roadmap line")
    if c["wide"]: notes.append(f"{c['wide']} code line(s) over 52 chars")
    print(f"  {c['words']:6}  {c['title'][:50]}")
    for n in notes: print(f"          - {n}")

def sentence(p, last=False):
    s = re.split(r"(?<=[.!?])\s+", re.sub(r"[*_`]", "", p).strip())
    return (s[-1] if last else s[0])[:110]

print("== First / last sentence of each chapter (read top to bottom)")
for c in body:
    print(f"  # {c['title'][:60]}\n    > {sentence(c['paras'][0])}\n    < {sentence(c['paras'][-1], True)}")
