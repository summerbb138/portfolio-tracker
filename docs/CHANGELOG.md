# Changelog — Portfolio Tracker

Module-level change record. System-level context: ICC `docs/SYSTEM_DOCUMENTATION.md` §Change Log; review reports in ICC `docs/`.

---

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
