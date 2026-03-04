# Bug Hunting Briefing — Login Not Working

**Date:** 2026-03-04
**Priority:** Frontend login fails despite backend running correctly

---

## Symptom

- Frontend shows the login page (design overhaul is complete and working)
- Backend IS running and healthy — uvicorn output confirms:
  ```
  12:18:21 | INFO | server.database | Connected to MongoDB: mongodb://localhost:27017 / fci_platform
  12:18:21 | INFO | server.main | Knowledge base loaded: 361341 core chars, 8 reference documents
  12:18:21 | INFO | server.main | FCI Platform ready — http://0.0.0.0:8000
  ```
- MongoDB IS running
- But entering username and clicking "Log In" fails
- Earlier Vite proxy error seen: `ECONNREFUSED` on `/api/auth/login`

## Most Likely Cause

The Vite dev server may need restarting. It was running during the design session and may have stale proxy state. The backend was down for a period (MongoDB stopped, then uvicorn wasn't started), and Vite's proxy may not have reconnected.

## Debugging Steps for Next Session

### Step 1: Restart the Vite dev server
```powershell
cd C:\coding\python_new\fci-investigator\fci-platform\client
# Ctrl+C to stop if running, then:
npm run dev
```

### Step 2: Check browser console for actual error
Open DevTools (F12) → Console tab and Network tab. Try logging in with `ben.investigator`. Look at:
- What URL is the request going to?
- What status code comes back?
- Is the request reaching the backend at all? (Check the uvicorn terminal for incoming requests)

### Step 3: Test the API directly (from PowerShell, not bash)
```powershell
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/auth/login -ContentType "application/json" -Body '{"username":"ben.investigator"}'
```
Should return user_id, username, display_name, token.

### Step 4: Check Vite proxy config
File: `client/vite.config.js`
```js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
},
```
The frontend makes requests to `/api/auth/login` and Vite proxies them to `http://localhost:8000/api/auth/login`.

### Step 5: Check if seed data exists
If the API returns a "user not found" type error:
```powershell
cd C:\coding\python_new\fci-investigator\fci-platform
python scripts/seed_demo_data.py
```
This creates 2 users (ben.investigator, demo.investigator) and 3 demo cases.

### Step 6: Check the login request/response format
Frontend sends: `POST /api/auth/login` with body `{"username": "ben.investigator"}`
- Login logic is in `server/routers/auth.py`
- Frontend API call is in `client/src/services/api.js`
- Auth state managed in `client/src/context/AuthContext.jsx`

## Key Files

| File | Purpose |
|------|---------|
| `server/main.py` | App entry, lifespan, CORS config |
| `server/routers/auth.py` | Login endpoint |
| `server/database.py` | MongoDB connection |
| `client/vite.config.js` | Proxy `/api` → localhost:8000 |
| `client/src/services/api.js` | Frontend API calls |
| `client/src/context/AuthContext.jsx` | Login state management |
| `scripts/seed_demo_data.py` | Seeds users + demo cases |

## What Was NOT Changed

**No backend code was modified this session.** The entire session was frontend design work (Binance Dark + Gold theme). The login issue is likely an infrastructure/proxy problem, not a code regression.

## Uncommitted Frontend Changes (6 files)

Final dark mode lightening + chat refinements — should be committed:
```
modified: client/index.html
modified: client/src/components/AppLayout.jsx
modified: client/src/components/investigation/ChatInput.jsx
modified: client/src/components/investigation/ChatMessageList.jsx
modified: client/src/components/shared/MarkdownRenderer.jsx
modified: client/src/index.css
```

## Related Docs
- Full design status: `/fci-platform/DESIGN_UPDATE_STATUS.md`
- Design spec: `/fci-platform/client/DESIGN_SPEC.md`
- Project orientation: `/fci-platform/CLAUDE.md`
