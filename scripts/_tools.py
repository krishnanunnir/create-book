"""Shared helpers for the book scripts: find a browser, screenshot a page,
convert an image, read an image's size. Works on macOS and Linux."""
import os, shutil, struct, subprocess, urllib.parse

MAC_BROWSERS = [
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
PATH_BROWSERS = ["brave-browser", "google-chrome", "google-chrome-stable",
                 "chromium", "chromium-browser", "microsoft-edge"]


def browser():
    """Path of a Chromium-family browser. BOOK_BROWSER overrides the search."""
    found = os.environ.get("BOOK_BROWSER") \
        or next((p for p in MAC_BROWSERS if os.path.exists(p)), None) \
        or next((shutil.which(n) for n in PATH_BROWSERS if shutil.which(n)), None)
    if not found:
        raise SystemExit("No Brave, Chrome, Chromium or Edge found. Set BOOK_BROWSER to its path.")
    return found


def screenshot(page, png, width, height, scale=1, wait_ms=0):
    """Headless screenshot of a local HTML file."""
    cmd = [browser(), "--headless", "--disable-gpu", "--hide-scrollbars",
           "--allow-file-access-from-files", f"--window-size={width},{height}",
           f"--force-device-scale-factor={scale}", f"--screenshot={png}"]
    if wait_ms:  # lets images finish loading
        cmd.append(f"--virtual-time-budget={wait_ms}")
    subprocess.run(cmd + ["file://" + urllib.parse.quote(os.path.abspath(page))],
                   check=True, capture_output=True)


def convert(src, dst, fmt, quality=90):
    """Convert an image to fmt ("png" or "jpeg"). True if it worked.
    Uses sips on macOS, ImageMagick elsewhere. An animated GIF gives its first frame."""
    magick = shutil.which("magick") or shutil.which("convert")
    if shutil.which("sips"):
        quality = ["-s", "formatOptions", str(quality)] if fmt == "jpeg" else []
        cmd = ["sips", "-s", "format", fmt, *quality, src, "--out", dst]
    elif magick:
        cmd = [magick, src + "[0]", "-quality", str(quality), f"{fmt}:{dst}"]
    else:
        raise SystemExit("Need sips (macOS) or ImageMagick to convert images.")
    return subprocess.run(cmd, capture_output=True).returncode == 0


def has_alpha(path):
    """True for a PNG that can hold transparent pixels (it may still be fully opaque)."""
    d = open(path, "rb").read()
    return d.startswith(b"\x89PNG") and (d[25] in (4, 6) or b"tRNS" in d[:max(d.find(b"IDAT"), 0)])


def is_animated(path):
    d = open(path, "rb").read()
    return d.startswith(b"GIF8") and d.count(b"\x21\xf9\x04") > 1  # one control block per frame


def flatten(src, dst):
    """Write src as a PNG on a white background, with no transparency. True if it worked."""
    magick = shutil.which("magick") or shutil.which("convert")
    if magick and not shutil.which("sips"):
        return subprocess.run([magick, src, "-background", "white", "-alpha", "remove",
                               "-alpha", "off", "png:" + dst], capture_output=True).returncode == 0
    # shortcut: sips has no flatten option, but its JPEG writer fills transparency with
    # white, so go through a quality-100 JPEG. Upgrade if the tiny loss ever shows.
    mid = dst + ".jpg"
    ok = convert(src, mid, "jpeg", quality=100) and convert(mid, dst, "png")
    if os.path.exists(mid):
        os.remove(mid)
    return ok


def image_size(path):
    """(width, height) of a PNG, GIF or JPEG, or None."""
    d = open(path, "rb").read()
    if d.startswith(b"\x89PNG"):
        return struct.unpack(">II", d[16:24])
    if d.startswith(b"GIF8"):
        return struct.unpack("<HH", d[6:10])
    if d.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 < len(d) and d[i] == 0xFF:
            marker, size = d[i + 1], struct.unpack(">H", d[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):  # a frame header
                h, w = struct.unpack(">HH", d[i + 5:i + 9])
                return w, h
            i += 2 + size
    return None
