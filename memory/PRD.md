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

## Current Known Environment State
- Database credentials are not configured in this workspace, so public/member pages may show the setup screen and admin bootstrap logs non-fatal DB-not-configured messages. This is expected until real DB config is present.

## Prioritized Backlog
### P0
- Configure/test against the real database environment to validate admin/member features end-to-end.
- Keep current `_bootstrap.php` load order and optional helper guards unchanged.

### P1
- Add stable admin/member test credentials after DB setup for repeatable auth testing.
- Review admin/member pages that still use older direct includes and gradually standardize them.

### P2
- Add a lightweight PHP regression script into CI/maintenance workflow for include-order and syntax checks.
- Improve setup-mode UI text if needed for non-technical admins.

## Next Tasks
- User can now share the exact page/button/screenshot issue list for the next targeted fixes.