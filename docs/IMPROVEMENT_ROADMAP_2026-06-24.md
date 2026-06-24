# Improvement Roadmap — 2026-06-24

यो roadmap project को वास्तविक codebase हेरेर बनाइएको हो।
यो Tailwind/Alpine adoption plan होइन, किनकि हालको repository मुख्य रूपमा
custom PHP + PDO + shared CSS architecture मा बनेको छ।

मुख्य सिद्धान्त:

1. चलिरहेको logic replace गर्ने होइन, duplicate हटाएर stable बनाउने
2. shared hosting-friendly रहिरहने
3. phase-wise सुधार गर्ने
4. हर phase पछि syntax/behavior validation गर्ने
5. public/admin/member तिनै portal मा shared code को ownership clear बनाउने

---

## 1. Verified Current State

### Stack reality

- Backend: custom PHP app, PDO-based MySQL/MariaDB access
- Frontend: large shared CSS bundles, handcrafted JS
- Tailwind CSS: active usage भेटिएन
- Alpine.js: active usage भेटिएन
- Bootstrap-style classes भने धेरै ठाउँमा छन्
- Shared hosting target: cPanel-friendly structure

### Current architecture facts

- Shared config को canonical file: `includes/config.php`
- Shared init layer: `core/init.php`
- Legacy/general bootstrap layer: `_bootstrap.php`
- Portal wrappers: `admin/_bootstrap.php`, `member/_bootstrap.php`
- Public chrome + nav logic: `includes/header.php`
- CSS layer: `app-core.css`, `app-public.css`, `app-admin.css`, `app-member.css`, `global-theme.php`

### Already completed in this phase

- public header legacy DOM remove गरिएको
- dead legacy header CSS ठूलो मात्रामा prune गरिएको
- dropdown cascade cleanup गरिएको
- quick-links dropdown markup normalize गरिएको
- `_bootstrap.php` phantom `/config` path हटाइएको
- `core/init.php` path constants idempotent बनाइएको
- `includes/config.php` output buffer + environment policy align गरिएको
- `admin/_bootstrap.php` र `member/_bootstrap.php` लाई `core/init.php` मा delegate गराइएको

### Execution Update (Latest)

- `assets/css/app-core.css` मा orphaned legacy comment cleanup गरिएको
- duplicated `.container-coop` early block remove गरेर canonical blockमा consolidate गरिएको
- exact duplicate utility/reset blocks machine-scan गरी safe prune गरिएको
- remaining exact duplicate rule groups पनि prune गरी re-scan पछि duplicate groups `0` confirm गरिएको

Recent pushed commits (safe CSS dedupe stream):

- `bbe133d` — orphaned field-coop comment cleanup
- `ac525be` — duplicated container-coop consolidation
- `a1aef96` — exact duplicate utility/reset block removal
- `f324d1f` — remaining exact duplicate rules prune

Validation notes:

- प्रत्येक step पछि `assets/css/app-core.css` diagnostics मा error-free result आएको छ
- edits ले business logic वा runtime PHP flow नछोई CSS redundancy मात्र घटाएको छ

### Execution Update (Bootstrap Consolidation)

- `core/init.php` मा shared bootstrap helpers विस्तार गरिएको:
	- local debug request detection
	- runtime error policy apply helper
	- optional include loader helper
	- member-auth include helper
	- exception forwarding helper
	- fatal type detection + shared fatal page renderer
- `admin/_bootstrap.php` र `member/_bootstrap.php` बाट repeated shutdown/exception logic significantly dedupe गरिएको
- fatal UI/flow behavior preserve गरिएको, र debug-detail escaping correctness bug पनि fix गरिएको

Recent pushed commits (bootstrap stream):

- `561b1b5` — local debug-request detection centralized
- `311d3ab` — runtime error policy shared across wrappers
- `ec8ac7d` — debug helper call simplification
- `6714bb6` — member-auth include consolidation
- `9893e18` — optional include dedupe in core init
- `68f5735` — exception forwarding shared
- `f29540d` — portal fatal-page renderer centralized
- `e073fdc` — debug-detail escaping fix post-consolidation
- `ae7bee5` — portal fatal/exception handler registration centralized
- `19fafef` — direct shared runtime policy call in wrappers

### Execution Update (Query Helper Consolidation)

- `core/init.php` मा `core_safe_count()` shared helper थपिएको छ (sqCount उपलब्ध हुँदा reuse, नभए safe fallback)
- Admin query-heavy modules मा repeated COUNT fallback pattern normalize गरिएको:
	- `admin/loan-applications.php`
	- `admin/kyc-applications.php`
	- `admin/vendor-enlistment.php`
	- `admin/member-online-portal.php`

Recent pushed commits (query helper stream):

- `bc4c3ce` — core_safe_count helper + loan/kyc count lines centralize
- `136f2e6` — vendor/member portal stats counts migrate to core_safe_count
- `9b71214` — analytics/messages count lines migrate to core_safe_count

---

## 2. Priority Model

### P0 — Stability First

यी काम break-risk कम र value high भएका छन्:

1. bootstrap duplication घटाउने
2. environment / error policy एउटै contract मा ल्याउने
3. dead header / dead CSS prune गर्ने
4. broad selectors scope गर्ने

### P1 — Shared Ownership Clear गर्ने

लक्ष्य:

- path constants को एक owner
- session policy को एक owner
- environment detection को एक owner
- DB access helpers को clear entry point

### P2 — Repeated Data Logic Reduce गर्ने

लक्ष्य:

- repeated query blocks identify गर्ने
- small reusable query helpers बनाउने
- dashboard/stat count queries standardize गर्ने

### P3 — CSS Architecture Professionalize गर्ने

लक्ष्य:

- repeated component classes consolidate गर्ने
- portal-specific overrides कम गर्ने
- global-theme मा canonical override strategy maintain गर्ने

### P4 — Security + Operations Hardening

लक्ष्य:

- auth flow consistency
- permission checks uniform बनाउने
- logs / backup / restore / deployment notes strengthen गर्ने

---

## 3. Phase-by-Phase Plan

## Phase A — Bootstrap Consolidation

### Goal

shared initialization लाई controlled र predictable बनाउने

### Remaining tasks

1. `_bootstrap.php`, `core/init.php`, `includes/config.php` बीच final ownership map document गर्ने
2. portal wrappers मा truly portal-specific code मात्र राख्ने
3. duplicated session/error/header policy जहाँ बाँकी छ त्यहाँ reduce गर्ने
4. `admin/_bootstrap.php` मा `$pdo` dependency लाई future-safe बनाउने

### Expected benefit

- white-screen risk कम
- local debugging predictable
- production behavior predictable
- onboarding easy

---

## Phase B — Data Access Cleanup

### Goal

same query patterns बारम्बार copy-paste भएको surface घटाउने

### Targets

1. admin dashboard stat queries
2. member profile / notification lookups
3. settings fetch patterns (`getSetting()` heavy areas)
4. repeated `try/catch + query + fetchColumn()` blocks

### Safe approach

- ORM introduce नगर्ने
- heavy framework introduce नगर्ने
- `includes/` वा `core/` मा small helper/service functions थप्ने
- public function names explicit राख्ने

### Example direction

- `adminDashboardCounts(PDO $pdo): array`
- `fetchRecentAttendanceStats(PDO $pdo): array`
- `memberUnreadNotificationCount(int $memberId): int`

---

## Phase C — Config and Environment Discipline

### Goal

shared hosting मा पनि safe र maintainable configuration behavior बनाउने

### Tasks

1. PHP version expectation document/update गर्ने
2. repo doc मा actual minimum supported PHP clear गर्ने
3. `database.local.php` / legacy `database.php` behavior स्पष्ट document गर्ने
4. environment values (`development`, `staging`, `production`) को effect document गर्ने

### Important note

हाल repo को codebase PHP 8+ oriented देखिन्छ।
यदि target hosting PHP 7.4 हो भने:

- backport decision explicit चाहिन्छ
- random compatibility assumption dangerous हुन्छ

त्यसैले roadmap अनुसार पहिले “policy clarity”, अनि मात्र “compatibility refactor”।

---

## Phase D — CSS / UI System Cleanup

### Goal

existing handcrafted CSS लाई component-oriented discipline मा लैजाने

### Tasks

1. shared button variants canonicalize गर्ने
2. card, table, dropdown, tabs का duplicate blocks reduce गर्ने
3. public/admin/member मा repeated responsive fixes compare गर्ने
4. `global-theme.php` लाई final override layer को रूपमा clean राख्ने

### Rule

Tailwind migrate गर्ने होइन।
यो codebase को लागि सही improvement:

- naming consistency
- duplicate removal
- cascade control
- smaller override surfaces

---

## Phase E — Auth / Permission Hardening

### Goal

access control logic predictable र testable बनाउने

### Tasks

1. admin gate rules review गर्ने
2. member gate rules review गर्ने
3. CSRF coverage compare गर्ने
4. page-level vs wrapper-level auth decisions separate गर्ने

### Expected benefit

- accidental bypass risk कम
- easier future maintenance
- cleaner portal boundaries

---

## Phase F — Shared Hosting Optimization

### Goal

cPanel/shared hosting मा fast, simple, low-risk deployment maintain गर्ने

### Tasks

1. auto-created directories सूची document गर्ने
2. writable path checklist बनाउने
3. backup/restore operational notes tighten गर्ने
4. no-build deployment rules document गर्ने

### Avoid

- Node build dependency compulsory बनाउने
- runtime-heavy framework introduce गर्ने
- complex queue/worker dependency थप्ने

---

## 4. Current Execution Order

अबको काम priority अनुसार यस्तो order मा जानुपर्छ:

1. bootstrap / wrapper duplication अझै reduce गर्ने
2. repeated admin/member DB query blocks extract गर्ने
3. PHP version policy clarify/document गर्ने
4. CSS shared component duplication reduce गर्ने
5. auth + permission consistency audit गर्ने

---

## 5. Break-Safe Working Rules

हरेक improvement गर्दा यी rules follow गर्नुपर्छ:

1. पहिले narrow surface identify गर्ने
2. small edit गर्ने
3. तुरुन्त syntax/test/behavior validation गर्ने
4. unrelated files नछुने
5. existing public API/paths preserve गर्ने
6. large rewrite नगर्ने
7. commit history phase-wise सानो राख्ने

---

## 6. Recommended Next Concrete Tasks

### Immediate next tasks

1. `admin/_bootstrap.php` मा `$pdo` dependence कम गर्ने preparation
2. admin dashboard repeated counts helper मा extract गर्ने
3. `includes/config.php` र `core/init.php` ownership boundary comments/documentation tighten गर्ने

### After that

4. shared query helper file introduce गर्ने
5. CSS component duplication अर्को high-impact slice मा reduce गर्ने

---

## 7. Success Criteria

यो roadmap सफल मानिने अवस्था:

- bootstrap path predictable हुन्छ
- config ownership clear हुन्छ
- repeated DB logic visibly कम हुन्छ
- header/nav/css regressions कम हुन्छन्
- portal wrappers thin हुन्छन्
- shared hosting deploy simple नै रहन्छ
- future refactor सानो commit series मा गर्न मिल्छ
