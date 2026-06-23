#!/usr/bin/env python3
"""Build the installable, S25-Ultra-optimized single-file app (index.html)
from the original roadmap HTML.

- Embeds a web app manifest + icons as data URIs (true single-file PWA so
  "Add to Home screen" gives a proper named app icon, even from file://).
- Adds iOS/Android web-app meta tags and safe-area (notch / gesture-bar) tuning.
- Best-effort inlines Google Fonts so the app is pixel-faithful fully offline;
  if the network is unavailable it leaves the original <link> untouched.
"""
import base64
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICONS = os.path.join(ROOT, "icons")
SRC = os.environ.get("SRC_HTML", os.path.join(HERE, "source-roadmap.html"))
OUT = os.path.join(ROOT, "index.html")


def b64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def png_data_uri(name):
    return "data:image/png;base64," + b64_file(os.path.join(ICONS, name))


def replace_once(html, old, new, label):
    n = html.count(old)
    if n != 1:
        raise SystemExit(f"[FAIL] anchor '{label}' found {n} times (expected 1)")
    return html.replace(old, new, 1)


# ── embedded manifest (data URI) ─────────────────────────────────────────────
# start_url/scope intentionally omitted: with a data: manifest they default to
# the document URL, which is correct both for file:// and when hosted.
def build_manifest_datauri():
    manifest = {
        "name": "Lock-in",
        "short_name": "Lock-in",
        "description": "A 24-month Pharma-Tech founder roadmap with weekly tasks and progress tracking.",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#0B1220",
        "theme_color": "#0B1220",
        "lang": "en",
        "dir": "ltr",
        "categories": ["education", "productivity"],
        "icons": [
            {"src": png_data_uri("icon-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": png_data_uri("icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": png_data_uri("icon-512-maskable.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    raw = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    return "data:application/manifest+json;base64," + base64.b64encode(raw).decode("ascii")


# ── external manifest for the optional hosted (GitHub Pages) path ─────────────
def write_external_manifest():
    manifest = {
        "name": "Lock-in",
        "short_name": "Lock-in",
        "description": "A 24-month Pharma-Tech founder roadmap with weekly tasks and progress tracking.",
        "start_url": "./",
        "scope": "./",
        "id": "./",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#0B1220",
        "theme_color": "#0B1220",
        "lang": "en",
        "dir": "ltr",
        "categories": ["education", "productivity"],
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open(os.path.join(ROOT, "manifest.webmanifest"), "w") as f:
        json.dump(manifest, f, indent=2)


# ── best-effort offline font inlining ────────────────────────────────────────
FONTS_CSS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700"
             "&family=Space+Grotesk:wght@400;500;600;700&display=swap")
UA = ("Mozilla/5.0 (Linux; Android 15; SM-S938B) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0.0.0 Mobile Safari/537.36")


def fetch(url, binary=False, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def inline_fonts():
    """Return a <style> block with base64 woff2 @font-face rules, or None."""
    try:
        css = fetch(FONTS_CSS)
    except Exception as e:
        print(f"[fonts] skip (cannot fetch CSS): {e}")
        return None
    # Keep only latin / latin-ext subsets to bound size.
    blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css)
    keep = [(sub, blk) for sub, blk in blocks if sub in ("latin", "latin-ext")]
    if not keep:
        print("[fonts] skip (no latin blocks parsed)")
        return None
    out = []
    for sub, blk in keep:
        m = re.search(r"src:\s*url\((https://[^)]+\.woff2)\)", blk)
        if not m:
            return None
        try:
            woff2 = fetch(m.group(1), binary=True)
        except Exception as e:
            print(f"[fonts] skip (cannot fetch woff2): {e}")
            return None
        data_uri = "data:font/woff2;base64," + base64.b64encode(woff2).decode("ascii")
        blk2 = blk.replace(m.group(1), data_uri)
        out.append(blk2)
    print(f"[fonts] inlined {len(out)} font files")
    return "  <style>\n" + "\n".join("    " + b for b in out) + "\n  </style>"


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        html = f.read()

    apple180 = png_data_uri("apple-touch-icon.png")
    icon192 = png_data_uri("icon-192.png")
    manifest_uri = build_manifest_datauri()

    # 1) viewport: better on-screen-keyboard behavior on Android
    html = replace_once(
        html,
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, interactive-widget=resizes-content">',
        "viewport",
    )

    # 2) web-app meta + icons + manifest (inserted after color-scheme)
    meta_block = (
        '  <meta name="color-scheme" content="dark">\n'
        '  <meta name="apple-mobile-web-app-capable" content="yes">\n'
        '  <meta name="mobile-web-app-capable" content="yes">\n'
        '  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
        '  <meta name="apple-mobile-web-app-title" content="Lock-in">\n'
        '  <meta name="application-name" content="Lock-in">\n'
        '  <meta name="description" content="A 24-month Pharma-Tech founder roadmap with weekly tasks and progress tracking — personal offline app.">\n'
        f'  <link rel="apple-touch-icon" sizes="180x180" href="{apple180}">\n'
        f'  <link rel="icon" type="image/png" sizes="192x192" href="{icon192}">\n'
        f'  <link rel="manifest" href="{manifest_uri}">'
    )
    html = replace_once(html, '  <meta name="color-scheme" content="dark">', meta_block, "meta-block")

    # 3) optional offline font inlining (replaces preconnect + stylesheet link)
    fonts_style = inline_fonts()
    if fonts_style:
        link_block = (
            '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">'
        )
        html = replace_once(html, link_block, fonts_style, "fonts-links")

    # 4) safe-area CSS (S25 notch / curved corners / gesture bar)
    css_add = (
        "      text-align: center;\n"
        "    }\n\n"
        "    /* ── Samsung Galaxy S25 Ultra: safe-area + app-shell tuning ───── */\n"
        "    body { overscroll-behavior: none; }\n"
        "    #root {\n"
        "      padding-left: env(safe-area-inset-left, 0px);\n"
        "      padding-right: env(safe-area-inset-right, 0px);\n"
        "    }\n"
        "  </style>"
    )
    html = replace_once(
        html,
        "      text-align: center;\n    }\n  </style>",
        css_add,
        "css-safe-area",
    )

    # 5) app shell height -> dynamic viewport (accounts for browser UI bars)
    html = replace_once(
        html,
        '    app: {\n      minHeight: "100vh",\n      background: "#0B1220",',
        '    app: {\n      minHeight: "100dvh",\n      background: "#0B1220",',
        "app-dvh",
    )
    html = replace_once(
        html,
        '      height: "100vh",\n      color: "#6F7E9C"',
        '      height: "100dvh",\n      color: "#6F7E9C"',
        "loading-dvh",
    )

    # 6) sticky header clears the status bar / punch-hole
    html = replace_once(
        html,
        '      padding: "14px 16px",\n      position: "sticky",',
        '      padding: "14px 16px",\n      paddingTop: "calc(14px + env(safe-area-inset-top, 0px))",\n      position: "sticky",',
        "header-safe-top",
    )

    # 7) content clears the bottom gesture bar
    html = replace_once(
        html,
        '    inner: {\n      maxWidth: 720,\n      margin: "0 auto"\n    },',
        '    inner: {\n      maxWidth: 720,\n      margin: "0 auto",\n      paddingBottom: "calc(28px + env(safe-area-inset-bottom, 0px))"\n    },',
        "inner-safe-bottom",
    )

    # 8) comfortable Android touch target on the primary button style
    html = replace_once(
        html,
        '      transition: "all 0.15s ease",\n      minHeight: 40\n    }),',
        '      transition: "all 0.15s ease",\n      minHeight: 44\n    }),',
        "btn-touch-target",
    )

    # 9) register the offline service worker only when hosted over http(s)
    html = replace_once(
        html,
        "root.render(React.createElement(App));\n</script>\n</body>",
        "root.render(React.createElement(App));\n</script>\n"
        "<script>\n"
        "  /* Offline caching when hosted over http(s); harmless no-op for file:// */\n"
        "  if ('serviceWorker' in navigator && location.protocol.indexOf('http') === 0) {\n"
        "    window.addEventListener('load', function () {\n"
        "      navigator.serviceWorker.register('./service-worker.js').catch(function () {});\n"
        "    });\n"
        "  }\n"
        "</script>\n</body>",
        "sw-register",
    )

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    write_external_manifest()
    kb = os.path.getsize(OUT) / 1024
    print(f"[ok] wrote {OUT} ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
