# Project Review & Critical Bug Fix PRD

## Original Problem Statement
"yo mero project ma kehi issue cha please fix gardinus la tapai project review garnus ani ma kehi issue list dinchu"

User later asked to start, selected a specific issue category, and prioritized fixing the most critical issue found during review.

## Architecture Decisions
- Existing project is a PHP cooperative website with public pages, admin portal, member portal, MySQL/PDO configuration, and shared bootstrap/config files.
- No framework migration was done; fix was intentionally minimal and targeted.
- Kept the existing database setup flow intact: public pages show setup message when DB credentials are missing; admin DB setup remains available.

## Implemented
- Fixed a critical bootstrap fatal error where `/app/_bootstrap.php` loaded `/app/core/helpers.php` before `/app/includes/config.php`, causing duplicate function declarations such as `sanitize()`.
- Updated `/app/_bootstrap.php` to load production config first and conditionally load optional legacy core files only when their sentinel functions are missing.
- Verified 272 PHP files with `php -l`; no syntax errors found.
- Verified key include flows: root index, member login, admin dashboard/bootstrap; no duplicate function fatal errors remain.
- 2026-06-08: Fixed KYC Nepal address dataset in `/app/includes/nepal-address.php` to 7 provinces, 77 districts, 753 unique local levels, with no duplicate municipality entries. Corrected known bad entries such as duplicate Rasuwa records, duplicate Rautahat record, invalid ward count for Dordi, typo in Pachaaljharana, and Kanchanpur Dodhara Chandani naming.
- 2026-06-08: Fixed public mobile menu interaction by stabilizing `assets/js/v9-mobile-fix.js`, adding dedicated dropdown chevron toggles, aria-expanded updates, close-state cleanup, and matching mobile CSS/test IDs in `/app/includes/header.php` and `/app/assets/css/app-public.css`.
- 2026-06-08: Added institutional profile fields in admin/public flow: other fund (`other_fund`), bank/cash balance (`bank_cash_balance`), fixed assets (`fixed_assets`), and total loan members (`total_loan_members`). Updated admin form, POST save/update logic, auto schema alters, fresh install SQL, ensure-admin-tables schema, and public display with null-safe fallbacks.
- 2026-06-08: Fixed KYC province dropdown duplication caused by repeated `initAllKYCCapture()` calls. Made `setupAddressDropdowns()` and same-address listener idempotent in `/app/assets/js/kyc-capture.js`, added cache-busting script version `v=10.9` in `/app/online-kyc.php`, and cleaned JS lint issues in the same file.
- 2026-06-08: Improved public institutional profile data-view UI/UX with compact bento-style stat cards, clearer fiscal-year header/date/document action, stronger financial hierarchy, readable indicator bars, mobile-responsive spacing, and required `data-testid` attributes for key interactive/user-facing elements.
- 2026-06-08: Improved admin institutional profile data-entry form UI/UX with compact control-room styling, stronger header, tighter grouped sections, cleaner input spacing, sticky save/cancel footer, mobile responsiveness, and additional `data-testid` attributes for important inputs/actions.
- 2026-06-08: Reworked public institutional profile data view from large bento cards to a compact ledger/table-style layout based on user screenshot feedback. Reduced header/card height, removed oversized stat cards, added dense rows for month-wise records, kept document action and indicators compact.
- 2026-06-08: Updated compact public institutional profile ledger to show two data items per row on desktop, reducing vertical height further while keeping mobile horizontal-scroll safety and preserving `data-testid` markers.
- 2026-06-08: Corrected the intended layout after user clarification: each month/report is now one table row, with all key metrics across columns (members, share capital, funds, savings, loan, bank/cash, fixed assets, total assets, indicators, document). This replaces the per-report multi-row ledger so month-wise data is clearer.
- 2026-06-08: Updated month-wise public institutional profile again per user clarification: desktop now shows two month/report cards per row, each card contains that month's compact metrics. Tablet/mobile falls back to one card per row.
- 2026-06-08: Fixed public mobile menu based on user screen recording: added final stable drawer CSS override to remove blur/grey wash, force opaque clear drawer, enforce modal backdrop above page content, prevent background clicks, make menu/close buttons explicit `type="button"`, cache-busted `v9-mobile-fix.js` to `v=9.11`, and changed mobile dropdown parents to toggle only instead of navigating to their page.
- 2026-06-08: Fixed notice popup desktop/mobile behavior: removed duplicate homepage popup markup (kept single global header popup), changed popup seen state from permanent `localStorage` to per-session `sessionStorage` so desktop does not stay hidden forever after one close, hid document/PDF button for photo-only notices, added cleaner photo-only image sizing, body scroll lock while popup is open, and added popup `data-testid` attributes.
- 2026-06-08: Added inline critical mobile menu fallback in `/app/includes/header.php` because the external mobile JS/cache path was still leaving hamburger clicks inactive on some mobile views. The fallback binds hamburger/close/backdrop/submenu directly, injects submenu chevrons, adds critical drawer CSS, and marks the menu as bound so the external script does not double-bind.
- 2026-06-08: Refined public institutional profile month cards per screenshot feedback: kept desktop two month/report cards per row, but restored the previous clearer inside-content style with serial number, icon, title, value/detail columns, plus chips for NPA/NPL/Liquidity.
- 2026-06-08: Cleaned up unused CSS remnants from earlier institutional profile layout iterations (old ledger/table/metrics/bento overrides) so the active two-card icon-ledger layout is easier to maintain. Created cPanel-safe update package `/app/aakash-coop-cpanel-update-2026-06-08.zip` with code only, excluding uploads/cache/logs/memory/test reports/tests/git metadata.
- 2026-06-08: **DEEP PROJECT REVIEW & CLEANUP** — fixed root cause of "create/list icons hidden by bottom color, only on hover" issue reported via screenshots:
    1. **Root cause**: `.btn { overflow:hidden }` in `app-core.css` (line 945) and `app-public.css` (line 4435) was clipping Devanagari text descenders (ँ, ी, ु) and bottom of icons inside green admin page-header buttons. Removed `overflow:hidden`, removed CSS ripple `::before` pseudo-element (depended on overflow), added `text-decoration:none !important` on `.btn` + `a.btn`.
    2. **Harmful neutralizer block removed**: `app-admin.css` lines 10629–10683 was forcing `background:#fff; color:#1f2937` on ALL `.btn-success/.btn-info/.btn-warning/.btn-secondary/.btn-outline-*` → broke colored buttons project-wide. Removed.
    3. **Final uniformity CSS appended to `assets/css/global-theme.php`** (loaded LAST so it beats everything): button overflow:visible + line-height 1.45 + min-height 38px for Devanagari safety; inactive nav-tabs on green strip use opaque white + text-shadow (fixes "वित्तीय रकम" white-on-green low contrast); admin-bottom-nav icons opacity:1 by default; stat-uniform-card icon color guaranteed visible per `data-bg` variant; all button icons `color:inherit` so they're never invisible.
    4. **Database deep-fix**: removed duplicate HRM module block (5 tables) in `database/install.sql`. The duplicate at lines 1896–2018 was a less-complete schema that ran first; the proper full schema at lines 2022+ was being skipped because of `IF NOT EXISTS`. Result: HRM employees table missing many columns on fresh installs. Fixed by removing the shorter duplicate so the full schema (employees + contracts + documents + education + experience + family + bank + history + internal_messages) is created. Total tables down from 79 to 74 (5 duplicates removed). Also normalized indentation on `institutional_profile` CREATE.
    5. **Unused files removed**: `assets/css/_color-vars.php` (@deprecated, replaced by `global-theme.php`), `assets/js/pwa-init.js` (zero references), `assets/js/v10.6-mobile-helpers.js` (zero references).
    6. **Regression suite extended**: added 4 new tests in `tests/test_php_feature_regression.py` for the four fixes above (overflow:hidden removed, final patch present, no duplicate HRM tables, neutralizer removed). All 11 tests pass.
    7. **PHP syntax check**: `php -l` clean across all 270 PHP files.

## Current Known Environment State
- Database credentials are not configured in this workspace, so public/member pages may show the setup screen and admin bootstrap logs non-fatal DB-not-configured messages. This is expected until real DB config is present.
- This fork is a legacy/custom PHP project. Supervisor React/FastAPI services are not applicable here and may show FATAL because `/app/frontend` and `/app/backend` do not exist.

## Prioritized Backlog
### P0
- Configure/test against the real database environment to validate admin/member features end-to-end.
- Keep current `_bootstrap.php` load order and optional helper guards unchanged.
- Validate the mobile public menu and online KYC dropdowns on the live DB-configured site where full pages render beyond setup mode.

### P1
- Add stable admin/member test credentials after DB setup for repeatable auth testing.
- Review admin/member pages that still use older direct includes and gradually standardize them.
- If the user provides any exact missing local-government list later, reconcile it against the current 753-level dataset.

### P2
- Add a lightweight PHP regression script into CI/maintenance workflow for include-order and syntax checks.
- Improve setup-mode UI text if needed for non-technical admins.

## Next Tasks
- With DB configured, test admin institutional profile add/edit and public profile rendering end-to-end.
- Continue with any next exact page/button/screenshot issue list from the user.

## Verification Log
- 2026-06-08: `php -l` passed for modified PHP files: `includes/nepal-address.php`, `includes/header.php`, `online-kyc.php`, `admin/institutional-profile.php`, `institutional-profile.php`, `admin/includes/ensure-admin-tables.php`.
- 2026-06-08: Address data CLI check passed: Municipalities=753, Unique=753, Duplicates=0.
- 2026-06-08: JS lint passed for `/app/assets/js/v9-mobile-fix.js`.
- 2026-06-08: Isolated Playwright DOM smoke confirmed mobile drawer open/close, chevron injection, submenu toggle, and aria-expanded update.
- 2026-06-08: Testing agent iteration 2 initially found null-safe public profile issue; fixed it and reran `/app/tests/test_php_feature_regression.py`: 7 passed.
- 2026-06-08: Verified KYC province dropdown repeated initialization in Playwright isolated DOM: after 5 manual re-inits, permanent province select stayed at 8 options total (placeholder + 7 provinces), with no duplicate province list.
- 2026-06-08: Verified institutional profile UI update with PHP syntax check, regression suite (`7 passed`), and browser smoke layout test showing no horizontal overflow at 1366px with sample data.
- 2026-06-08: Verified admin institutional profile UI update with PHP syntax check, regression suite (`7 passed`), and isolated browser layout smoke test showing no horizontal overflow at 1366px with sample admin form content.
- 2026-06-08: Verified compact ledger-style public institutional profile update with PHP syntax check, regression suite (`7 passed`), and isolated browser smoke test showing 9 compact ledger rows with no horizontal overflow at 1366px.
- 2026-06-08: Verified two-item-per-row ledger update with PHP syntax check, regression suite (`7 passed`), and isolated browser smoke showing 6-column table, 5 rows for 9 sample items, no horizontal overflow at 1366px.
- 2026-06-08: Verified month/report-per-row table layout with PHP syntax check, regression suite (`7 passed`), and isolated browser smoke showing 3 sample monthly rows, 11 columns, and no horizontal overflow at 1366px.
- 2026-06-08: Verified two-month-per-row grid layout with PHP syntax check, regression suite (`7 passed`), and isolated browser smoke confirming first two month cards share the same row and the third wraps to the next row.
- 2026-06-08: Verified mobile menu fix with PHP syntax checks, JS lint (`0 blocking`), regression suite (`7 passed`), video analysis, and isolated mobile DOM tests confirming drawer opens with modal backdrop, parent dropdown toggle prevents navigation, and close/backdrop logic removes open state.
- 2026-06-08: Verified notice popup fix with PHP syntax checks, JS lint (`0 blocking`), regression suite (`7 passed`), desktop browser smoke confirming popup shows and close writes `sessionStorage`, and mobile browser smoke confirming photo-only popup image displays correctly.
- 2026-06-08: Verified inline mobile menu fallback with PHP syntax check, regression suite (`7 passed`), and mobile browser smoke confirming hamburger click opens drawer, backdrop activates, parent dropdown opens without navigating, and submenu displays.
- 2026-06-08: Verified institutional profile two-card icon-ledger layout with PHP syntax check, regression suite (`7 passed`), and browser smoke confirming two month cards in one row with 18 icon-ledger rows total for 2 sample cards.
- 2026-06-08: Verified cPanel update ZIP contents exclude live data/runtime folders, PHP syntax checks pass for key modified pages, regression suite (`7 passed`), and SHA256 checksum is `44743f8750cc5301d139b1529901e4ebe59e6d5805ac90c608e0f7af6e1dfd62`.