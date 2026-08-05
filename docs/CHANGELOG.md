# Changelog — Portfolio Tracker

Module-level change record. System-level context: ICC `docs/SYSTEM_DOCUMENTATION.md` §Change Log; review reports in ICC `docs/`.

---

## 2026-08-04 — Public Pages hosting restored + history scrubbed (no app-code change)

- **Root cause of broken iPhone updates:** the repo had been switched to private, which auto-disabled GitHub Pages on the free plan (Pages needs a public repo there). Live URL returned "Site not found"; the cached PWA kept running so it went unnoticed.
- **Data privacy:** real holdings existed in early git history (seed data, removed in 5ad50e0). Reset history to a single clean commit (orphan branch + force-push), hardened `.gitignore`, genericized doc ticker examples (AAPL/Toyota), removed the stale PDF. Then made the repo public and enabled Pages. Verified live: `data/my-portfolio.json` and the PDF 404; remote tree has no real tickers.
- **Residual:** old commits are dangling (fetchable only by exact, non-discoverable SHA). Full purge = delete+recreate the repo (needs `delete_repo`).
- **Deploy fix:** added root `index.html` redirect to `/pwa/` (app had moved to `/pwa/`, leaving the Pages root URL empty).
- Full procedure + future reminders: system doc §26.

## 2026-08-04 — v1.5 (build 25): Cost includes cash

- **Cost now includes cash balances** in both the PWA and the ICC feeder, matching Value (which already included cash). P&L is unchanged (cash cancels on both sides); Return is now measured against total account capital (stock cost + cash).
- **ICC feeder P&L bug fixed as a side effect:** `pwa/server.py` `build_portfolio()` previously added cash to `totalValue` but not `totalCost`, overstating `totalPL` by the cash balance. `total_cost += cash_usd` now corrects it.
- Version bumped 1.4 → 1.5 across UI badge, `server.py`, ICC registry (`CLAUDE.md`), and system doc. UI build number realigned to the SW cache version (badge had drifted at build 8 while `sw.js`/root `sw.js` reached v25).
- Files: `pwa/index.html` (`render()`), `pwa/server.py`, `pwa/sw.js` + root `sw.js` (v24→v25).

## 2026-07-05/06 — Fresh-pass review fixes

- **Localhost-only:** the http.server backend binds `127.0.0.1` (system-wide network-posture decision).
- **`logs/` untracked** in git (startup logs kept the working tree permanently dirty) and gitignored.
- Full report: ICC `docs/SYSTEM_REVIEW_2026-07-05.md`.

## 2026-07-02/05 — Hardening + fixes (from git)

- `pwa/server.py` (backend) tracked in git; silent quote/FX fetch failures now logged (R3).
- Version sync: single source of truth across doc, code, UI badge, and ICC registry; system doc PDF regenerated (reportlab generator retired).
- Standard `/api/health` endpoint with quiet health-check logging.
- v1.4 build 8: active tab uses darker blue for clear selection.

Older detail: `git log` in this repo.
