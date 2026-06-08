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