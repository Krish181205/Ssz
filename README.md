# 💊 Pharma-Tech Founder Mentor — Personal App

A 24-month, day-by-day founder roadmap (188 tasks across 5 phases) packaged as a
private, **installable, offline app** — tuned for the **Samsung Galaxy S25 Ultra**.

This is for **personal use only**. It is **not** published to the Play Store or
any other platform. The whole app lives in a single self-contained file.

---

## 📱 Put it on your S25 Ultra (recommended: single file)

The app is one file — [`index.html`](index.html). Everything (the React app,
all 188 tasks, fonts, the app icon, and the web-app manifest) is embedded, so it
runs **fully offline** with **zero internet** once it's on your phone.

1. **Transfer `index.html` to the phone** — email it to yourself, drop it in
   Google Drive, or copy it over USB. Save it somewhere like `Downloads`.
2. **Open it** with **Chrome** or **Samsung Internet** (tap the file → open with
   a browser).
3. **Install it as an app** (gives it a real icon + full-screen, no address bar):
   - **Samsung Internet:** tap the **≡ menu** → **Add page to** → **Home screen**.
   - **Chrome:** tap the **⋮ menu** → **Add to Home screen** → **Install / Add**.
4. You'll get a **“Founder Mentor”** icon (the teal/violet capsule) on your home
   screen. Launch it like any other app.

Your progress is saved on the device (in the browser's local storage), so ticking
off tasks persists between launches.

> **Tip:** Use **“Save Backup”** inside the app every so often. If you ever
> reinstall or move phones, **“Restore”** brings your progress back.

---

## 🎯 What was optimized for the S25 Ultra

- **Installable PWA**: embedded web-app manifest + maskable app icons → real
  home-screen icon, standalone full-screen launch, dark theme (`#0B1220`) status
  bar.
- **Safe areas**: the sticky header clears the **status bar / punch-hole camera**
  (`env(safe-area-inset-top)`), and content clears the **gesture navigation bar**
  at the bottom (`env(safe-area-inset-bottom)`), with side insets for landscape.
- **Dynamic viewport** (`100dvh`) so the layout fills the tall 19.5:9 screen
  correctly as the browser bars show/hide.
- **Offline fonts**: *IBM Plex Sans* and *Space Grotesk* are inlined — no network
  fetch, no font “pop-in”, identical look offline.
- **Touch & feel**: comfortable 44 px tap targets, no pull-to-refresh/overscroll
  bounce, smooth keyboard handling (`interactive-widget=resizes-content`).

---

## 🤖 About the “Ask AI Mentor” button

Each task has an optional **Ask AI Mentor** button. It calls Anthropic's API, so
it needs **internet** and an **API key**. Offline (or without a key) it shows a
friendly message and everything else keeps working. Want it functional on the
phone with your own key? Say the word and I'll add a small key field.

---

## 🌐 Optional: host it as a full PWA (e.g. GitHub Pages)

Not required for personal use, but if you serve the repo over HTTPS you also get
service-worker offline caching and a “true” installable PWA:

1. Repo **Settings → Pages → Deploy from branch** → pick this branch, root.
2. Open the published `https://…/index.html` on the phone and **Add to Home
   screen**. The included `service-worker.js` + `manifest.webmanifest` activate
   automatically (they're ignored when you just open the file directly).

---

## 🛠 Repo contents / rebuilding

| Path | What it is |
|------|------------|
| `index.html` | **The app.** Self-contained, offline, install-ready. This is the file you put on the phone. |
| `manifest.webmanifest` | External manifest for the hosted-PWA path. |
| `service-worker.js` | Offline cache for the hosted-PWA path (no-op on `file://`). |
| `icons/` | Generated app icons (192/512/maskable/apple-touch). |
| `tools/source-roadmap.html` | The original source the app is built from. |
| `tools/make_icons.py` | Regenerates the capsule app icons. |
| `tools/build_app.py` | Applies all PWA + S25 tuning and writes `index.html`. |

Rebuild after editing the source or icons:

```bash
python3 tools/make_icons.py     # only if you change the icon
python3 tools/build_app.py      # writes index.html (inlines fonts if online)
```

The build is verified by syntax-checking every inline script and mounting the app
in a headless DOM to confirm it renders with no runtime errors.
