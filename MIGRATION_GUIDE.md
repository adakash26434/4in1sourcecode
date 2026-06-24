# MIGRATION GUIDE — Project Audit Improvements v3.0

**Status:** Ready for deployment  
**Breaking Changes:** ⚠️ Minor - bootstrap files need update  
**Rollback Plan:** Git reset to previous branch  

---

## OVERVIEW

This guide explains how to migrate from the old scattered architecture to the new unified system created in the audit.

**Changes:**
- ✅ CSS consolidated into 3 core files
- ✅ Admin UI components unified
- ✅ Bootstrap system centralized
- ✅ Form/table components improved
- 🔄 Inline event handlers need migration (future)

---

## PHASE 1: IMMEDIATE (No Breaking Changes)

These changes are **non-breaking** and can be deployed immediately.

### 1.1 New CSS System

**Files Added:**
- `assets/css/global.css` - Core design system (load first)
- `assets/css/forms-tables.css` - Form/table components (load after global)
- `assets/css/admin-ui-unified.css` - Admin UI styles (load after forms-tables)

**HTML Update:**
```html
<!-- Load in this order -->
<link rel="stylesheet" href="/assets/vendor/bootstrap.min.css">
<link rel="stylesheet" href="/assets/css/global.css">
<link rel="stylesheet" href="/assets/css/forms-tables.css">
<link rel="stylesheet" href="/assets/css/admin-ui-unified.css">

<!-- Old files (can be kept for backward compatibility, but will be removed later) -->
<!-- <link rel="stylesheet" href="/assets/css/app-core.css"> -->
<!-- <link rel="stylesheet" href="/assets/css/app-admin.css"> -->
<!-- <link rel="stylesheet" href="/assets/css/app-member.css"> -->
```

**No Action Required:** Old CSS files still work. New CSS is supplementary.

### 1.2 New Admin UI Components

**File Added:**
- `includes/admin-ui-unified.php` - 10 core UI components

**Usage in Admin Pages:**

Before:
```php
<?php
// Scattered UI logic
echo '<div class="admin-card">';
echo '<h5 class="admin-card-title">Title</h5>';
echo '<div class="admin-card-body">';
// ... content ...
echo '</div></div>';
?>
```

After:
```php
<?php
require_once BASEDIR . '/includes/admin-ui-unified.php';

// Unified component API
echo adminCard('Page Title', 'fa-cog', 'This is cleaner.');
?>
```

**Available Components:**
```php
adminHeader($title, $icon, $subtitle, $rightHtml, $color)  // Page header
adminCard($title, $icon, $body, $footer, $class)           // Card container
adminAlert($type, $message, $dismissible)                  // Alert box
adminBadge($text, $type, $icon)                            // Status badge
adminButton($text, $url, $type, $icon, $class)             // Button/link
adminStatCard($value, $label, $icon, $color, $trend)       // Metric card
adminEmpty($icon, $title, $message, $action)               // Empty state
adminFooter($submitText, $submitType, $cancelUrl, $extra)  // Form footer
_t($nepali, $english)                                       // Translation helper
```

**No Action Required:** Old functions in `admin/includes/admin-ui.php` still work.

### 1.3 Improved Form & Table Components

**Files Modified:**
- `includes/components/form-section.php` - Added info text support
- `includes/components/data-table.php` - Added sortable/paginated support

**New Usage:**

Form section with info:
```php
<?php
$formSectionTitle = 'व्यक्तिगत जानकारी';
$formSectionIcon  = 'fa-user';
$formSectionInfo  = 'यो खेत अनिवार्य छ।';  // NEW
include __DIR__ . '/../includes/components/form-section.php';
?>
<!-- fields -->
<?php include __DIR__ . '/../includes/components/form-section-close.php'; ?>
```

Table with search:
```php
<?php
$tableHeaders = ['Name', 'Email', 'Status'];
$tableId      = 'membersTable';
$tableSearch  = true;   // NEW - enables search box
$tableSortable = true;  // NEW - enable sorting headers
include __DIR__ . '/../includes/components/data-table.php';
?>
<!-- table rows -->
<?php include __DIR__ . '/../includes/components/data-table-close.php'; ?>
```

**No Action Required:** Old syntax still works (backward compatible).

---

## PHASE 2: DEPLOYMENT (Minor Breaking Change)

This phase requires updating bootstrap files.

### 2.1 Update Root Bootstrap (`_bootstrap.php`)

**File:** `/vercel/share/v0-project/_bootstrap.php`

**Old Content:**
```php
<?php
// Multiple requires for config, auth, helpers
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/core/helpers.php';
// ... more requires ...
?>
```

**New Content:**
```php
<?php
// UNIFIED BOOTSTRAP SYSTEM v3.0
require_once __DIR__ . '/includes/bootstrap-unified.php';
bootstrapApplication('public');
?>
```

**Change Required:** ✅ 1 file change

### 2.2 Update Admin Bootstrap (`admin/_bootstrap.php`)

**File:** `/vercel/share/v0-project/admin/_bootstrap.php`

**Old Content:**
```php
<?php
require_once __DIR__ . '/../includes/config.php';
// error handling ...
?>
```

**New Content:**
```php
<?php
// UNIFIED BOOTSTRAP SYSTEM v3.0
require_once dirname(__DIR__) . '/includes/bootstrap-unified.php';
bootstrapApplication('admin');
?>
```

**Change Required:** ✅ 1 file change

### 2.3 Update Member Bootstrap (`member/_bootstrap.php`)

**File:** `/vercel/share/v0-project/member/_bootstrap.php`

**Old Content:**
```php
<?php
require_once __DIR__ . '/../includes/config.php';
// error handling ...
?>
```

**New Content:**
```php
<?php
// UNIFIED BOOTSTRAP SYSTEM v3.0
require_once dirname(__DIR__) . '/includes/bootstrap-unified.php';
bootstrapApplication('member');
?>
```

**Change Required:** ✅ 1 file change

---

## TESTING CHECKLIST

After deploying, test these scenarios:

### CSS & UI
- [ ] Public page loads without CSS errors
- [ ] Admin panel displays correctly
- [ ] Member portal loads properly
- [ ] Forms render with proper spacing
- [ ] Tables responsive on mobile (card view)
- [ ] Nepali text displays correctly

### Bootstrap System
- [ ] Root page loads (public)
- [ ] Admin page loads with `?debug=1` shows no errors
- [ ] Member page loads with `?debug=1` shows no errors
- [ ] Session handling works across contexts
- [ ] Error pages display on 500 error

### Admin UI Components
- [ ] `adminHeader()` renders correctly
- [ ] `adminCard()` with/without body works
- [ ] `adminAlert()` dismisses properly
- [ ] `adminBadge()` colors correct
- [ ] `adminStatCard()` trends display
- [ ] `adminEmpty()` with action button works

### Security
- [ ] Security headers present (check Dev Tools)
- [ ] HTTPS enforced on login forms
- [ ] Session cookies HTTPOnly and SameSite
- [ ] CSRF tokens present in forms

### Performance
- [ ] Page load time reasonable
- [ ] No JavaScript console errors
- [ ] CSS loaded without 404s
- [ ] Images load correctly

---

## ROLLBACK PLAN

If issues arise, rollback is simple:

**Option 1: Git Revert**
```bash
git revert HEAD~8  # If commits pushed
# or
git reset --hard HEAD~8  # If not yet pushed
```

**Option 2: Manual Restore**
1. Delete new files:
   - `includes/bootstrap-unified.php`
   - `includes/admin-ui-unified.php`
   - `assets/css/global.css`
   - `assets/css/forms-tables.css`
   - `assets/css/admin-ui-unified.css`

2. Restore original bootstrap files from backup

3. Remove CSS links from HTML headers

---

## FILE MAPPING

### New Files (Safe to Delete)
```
✅ assets/css/global.css                 - 736 lines
✅ assets/css/forms-tables.css           - 473 lines
✅ assets/css/admin-ui-unified.css       - 343 lines
✅ includes/admin-ui-unified.php         - 362 lines
✅ includes/bootstrap-unified.php        - 382 lines
✅ AUDIT_REPORT_v3.md                    - Documentation
✅ MIGRATION_GUIDE.md                    - This file
```

### Modified Files (Backward Compatible)
```
✏️ includes/components/form-section.php          - Enhanced
✏️ includes/components/data-table.php            - Enhanced
```

### Old Files (Can Still Use)
```
📌 _bootstrap.php                     - Original still works
📌 admin/_bootstrap.php               - Original still works
📌 member/_bootstrap.php              - Original still works
📌 assets/css/app-core.css            - Still loaded (may remove later)
📌 assets/css/app-admin.css           - Still loaded (may remove later)
📌 assets/css/app-member.css          - Still loaded (may remove later)
📌 admin/includes/admin-ui.php        - Still available
```

---

## FUTURE IMPROVEMENTS (Phase 3)

After this deployment stabilizes, next phase includes:

1. **Remove Inline Event Handlers** (Critical)
   - Migrate 200+ `onclick=` attributes
   - Create `assets/js/admin-events.js` with event delegation
   - Test all admin interactions

2. **Consolidate Duplicate Functions** (Important)
   - Merge `core/helpers.php` into `includes/helpers.php`
   - Single location for all utilities
   - Clear function organization

3. **Database Audit** (Medium)
   - Document schema with ERD
   - Establish naming conventions
   - Create query builder helper

4. **Accessibility Audit** (Medium)
   - WCAG 2.1 AA compliance check
   - Add missing ARIA attributes
   - Keyboard navigation testing

---

## DEPLOYMENT INSTRUCTIONS

### For Development Environment
```bash
# 1. Stash any local changes
git stash

# 2. Pull latest changes
git pull origin main

# 3. Clear cache if using any
rm -rf /path/to/cache/*

# 4. Test locally
# Navigate to http://localhost:5000 and test

# 5. If issues, rollback
git reset --hard HEAD~1
```

### For Staging/Production
```bash
# 1. Create backup
mysqldump -u user -p database > backup-2026-06-24.sql

# 2. Pull changes
git pull origin main

# 3. Deploy
# Your deployment script here

# 4. Verify
# Check admin panel, member portal, public site

# 5. If issues, restore from backup
# Your rollback script here
```

---

## SUPPORT & QUESTIONS

If you encounter issues:

1. **Check error logs:**
   - `logs/error.log` (PHP errors)
   - `logs/php_errors.log` (startup errors)
   - Browser console (JS errors)

2. **Test with debug mode:**
   - Admin: `http://localhost:5000/admin/dashboard.php?debug=1`
   - Shows detailed error messages

3. **Contact:**
   - Senior developer on team
   - Reference AUDIT_REPORT_v3.md for details
   - Check this MIGRATION_GUIDE.md for resolution steps

---

## SUMMARY

| Item | Status | Impact | Action |
|------|--------|--------|--------|
| CSS Consolidation | ✅ Ready | Medium | Deploy anytime |
| Admin UI Unification | ✅ Ready | Medium | Deploy anytime |
| Bootstrap Refactor | ✅ Ready | Low | Requires 3 file edits |
| Form/Table Components | ✅ Ready | Low | Backward compatible |
| Inline Event Handlers | 🔄 Pending | High | Next phase |
| Function Consolidation | 🔄 Pending | Medium | Next phase |

---

*Migration Guide v1.0*  
*Last Updated: 2026-06-24*  
*Prepared for v0 Deployment*
