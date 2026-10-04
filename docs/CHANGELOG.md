# Changelog — Portfolio Tracker

Module-level change record. System-level context: ICC `docs/SYSTEM_DOCUMENTATION.md` §Change Log; review reports in ICC `docs/`.

---

## 2026-10-03 — v1.5 (build 27): self-hosted fetch relay (Cloudflare Worker)

- **What broke:** The iPhone app stopped updating on 2026-09-13. Root cause: the free public CORS proxies died — corsproxy.io dropped anonymous keyless access (403 `keyless_legacy_url`; API key now required) and api.allorigins.win was down (CDN 522). The Mac copy was unaffected (`server.py` fetches Yahoo directly).
- **Fix:** Quotes now route through our own Cloudflare Worker, `portfolio-relay` (`https://portfolio-relay.summerbb138.workers.dev`), on the free tier (100k requests/day). The Worker forwards only Yahoo Finance v8 chart URLs, answers CORS only for the app's GitHub Pages origin (`localhost:8091` also allowed for local dev), refuses everything else, logs nothing, and never caches (`Cache-Control: no-store`).
- **Files:** `pwa/index.html` (`CORS_PROXIES` → single worker entry), `pwa/sw.js` + root `sw.js` (relay host added to the fetch bypass so quote JSON is never cached), `pwa/version.js` (`APP_BUILD` 26 → 27). Relay account: Cloudflare free plan, summerbb138@gmail.com — reusable by future browser-based fetchers in the fleet.
- **Verified:** relay returns live quotes (AAPL/US, SHOP.TO/CA, 7203.T/JP incl. 5-day history); non-Yahoo targets rejected with 403; live site serves build 27; iPhone refresh confirmed by user.
- **Docs:** system documentation §11/§19/§20 updated; PDF regenerated with the shared `md_to_pdf.py`.

## 2026-08-04 — v1.5 (build 26): foolproofing (version source, data location, backups, hook)

- **One version source:** `pwa/version.js` (`APP_VERSION`/`APP_BUILD`). `sw.js` `importScripts` it and derives the cache name; `index.html` stamps the badge; `server.py` and the ICC (`shell/web.py` `_pwa_version()`) parse it. Bump one file to release.
- **Live data outside the repo:** `server.py` now reads/writes `~/Library/Application Support/PortfolioTracker/my-portfolio.json` — cannot be committed. Migrated the real file there.
- **Rotating backups:** `server.py` writes timestamped copies to `data/backups/` (last 10) on every sync — gitignored but inside `~/Desktop/Claude Summary`, so the ICC backup tar captures them.
- **Pre-push hook:** `scripts/githooks/pre-push` (activate: `git config core.hooksPath scripts/githooks`) aborts any push containing portfolio-data-shaped JSON; tested.
- **Docs:** PDF regenerated via shared `md_to_pdf.py` (bespoke `generate_pdf.py` retired). Full detail: system doc §26.6–26.7.

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
