# How to Convert Go Ai into APK, EXE, or Web App (Free)

Go Ai is already a **PWA (Progressive Web App)** — it can be installed directly from the browser on both mobile and desktop. Below are all the free methods to distribute it.

---

## Method 1 — Install as Web App / PWA (Easiest, FREE)

Your app already has a `manifest.json` and `sw.js` — it's a PWA!

### On Android (Chrome):
1. Open your deployed Go Ai URL in Chrome
2. Tap the **⋮ menu** → **"Install app"** or **"Add to Home screen"**
3. It will appear as a standalone app with your logo icon

### On iPhone (Safari):
1. Open Go Ai URL in Safari
2. Tap **Share button** → **"Add to Home Screen"**
3. It opens like a native app (no browser bar)

### On Windows/Mac/Linux (Chrome or Edge):
1. Open Go Ai URL in Chrome/Edge
2. Click the **install icon** in the address bar (or Menu → Install)
3. It opens as a standalone desktop window

**This is the simplest and best approach — no APK or EXE needed.**

---

## Method 2 — Android APK (Free)

### Option A: No-Code APK Builders (Easiest)

1. **Deploy Go Ai online first** (see DEPLOY.md — use Railway, Render, or Fly.io)
2. Use a free **WebView APK builder**:
   - [WebIntoApp](https://webintoapp.com) — Free, produces APK
   - [AppsGeyser](https://appsgeyser.com) — Free, easy to use
   - [GoNative.io](https://gonative.io) — Free trial
3. Enter your deployed URL (e.g. `https://go-ai.up.railway.app`)
4. Upload `logo.png` as the app icon
5. Download your `.apk` file
6. Share the APK or install directly on any Android phone

### Option B: Capacitor (Developer Method)

Requires: Node.js + Android Studio (both free)

```bash
# In the Go Ai project folder:
npm init -y
npm install @capacitor/core @capacitor/android
npx cap init "Go Ai" com.goprojects.goai --web-dir static
```

Edit `capacitor.config.json`:
```json
{
  "appId": "com.goprojects.goai",
  "appName": "Go Ai",
  "webDir": "static",
  "server": {
    "url": "https://YOUR-DEPLOYED-URL.up.railway.app",
    "cleartext": false
  }
}
```

Build:
```bash
npx cap add android
npx cap open android
```
In Android Studio → Build → Build APK.

---

## Method 3 — Windows EXE (Free)

### Option A: Electron (Recommended)

```bash
# Create a new folder for the EXE build
mkdir go-ai-desktop
cd go-ai-desktop
npm init -y
npm install electron --save-dev
```

Create `main.js`:
```javascript
const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: 'logo.png',
    title: 'Go Ai',
    webPreferences: { nodeIntegration: false }
  });
  // Point to your deployed URL
  win.loadURL('https://YOUR-DEPLOYED-URL.up.railway.app');
  // Or load local files: win.loadFile('static/index.html');
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
```

Update `package.json`:
```json
{
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "npx electron-builder --win"
  }
}
```

Build EXE:
```bash
npm install electron-builder --save-dev
npx electron-builder --win
```

The `.exe` will be in the `dist/` folder.

### Option B: Nativefier (Quick one-liner)

```bash
npx nativefier "https://YOUR-DEPLOYED-URL" --name "Go Ai" --icon logo.png
```

This creates a standalone `.exe` app from any URL. Free and open source.

---

## Method 4 — Deploy as Web App (Free Hosting)

See `DEPLOY.md` for full details. Quick options:

| Platform | Cost | URL |
|----------|------|-----|
| Railway | Free tier | railway.app |
| Render | Free tier | render.com |
| Fly.io | Free tier | fly.io |
| Koyeb | Free tier | koyeb.com |

---

## Important Notes

- **Phone/desktop must have internet** — the app connects to your server for AI
- **PWA is the best free option** — works everywhere, no app store needed
- For **Google Play Store**: you need a $25 one-time fee + signed APK + privacy policy
- `localhost` does NOT work inside APK on phones — you must deploy online first
