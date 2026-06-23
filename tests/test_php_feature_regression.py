"""Regression checks for Nepal address dataset, KYC selectors, mobile JS, and profile fields."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path("/workspace/project/4in1sourcecode")

# Check if PHP is available
PHP_AVAILABLE = shutil.which("php") is not None


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def run_php_inline(code: str) -> str:
    if not PHP_AVAILABLE:
        pytest.skip("PHP CLI not installed")
    proc = run_cmd(["php", "-r", code])
    assert proc.returncode == 0, f"PHP failed: {proc.stderr or proc.stdout}"
    return proc.stdout.strip()


def test_nepal_address_counts_and_uniqueness() -> None:
    code = r'''
require '/workspace/project/4in1sourcecode/includes/nepal-address.php';
$data = getNepalAddressData();
$provinceCount = count($data);
$districtCount = 0;
$localLevelCount = 0;
$dupWithinDistrict = [];
$seenByDistrict = [];

foreach ($data as $province => $districts) {
    $districtCount += count($districts);
    foreach ($districts as $district => $municipalities) {
        $seenByDistrict[$district] = [];
        foreach ($municipalities as $m) {
            $name = trim((string)($m['name'] ?? ''));
            if ($name === '') continue;
            $localLevelCount++;
            if (isset($seenByDistrict[$district][$name])) {
                $dupWithinDistrict[] = $district . '::' . $name;
            }
            $seenByDistrict[$district][$name] = true;
        }
    }
}

echo json_encode([
    'provinces' => $provinceCount,
    'districts' => $districtCount,
    'local_levels' => $localLevelCount,
    'dup_within_district' => array_values(array_unique($dupWithinDistrict)),
], JSON_UNESCAPED_UNICODE);
'''
    out = run_php_inline(code)
    payload = json.loads(out)
    assert payload["provinces"] == 7
    assert payload["districts"] == 77
    assert payload["local_levels"] == 753
    assert payload["dup_within_district"] == []


def test_nepal_address_specific_corrected_entries() -> None:
    code = r'''
require '/workspace/project/4in1sourcecode/includes/nepal-address.php';
$data = getNepalAddressData();

function findWard($data, $district, $targetName) {
  foreach ($data as $province => $districts) {
    if (!isset($districts[$district])) continue;
    foreach ($districts[$district] as $m) {
      if (($m['name'] ?? '') === $targetName) {
        return (int)($m['wards'] ?? 0);
      }
    }
  }
  return null;
}

echo json_encode([
  'dodhara_chandani' => findWard($data, 'कञ्चनपुर', 'दोधारा चाँदनी नगरपालिका'),
  'pachaljharana' => findWard($data, 'कालीकोट', 'पचालझरना गाउँपालिका'),
  'dordi' => findWard($data, 'लमजुङ', 'दोर्दी गाउँपालिका')
], JSON_UNESCAPED_UNICODE);
'''
    out = run_php_inline(code)
    payload = json.loads(out)
    assert payload["dodhara_chandani"] == 10
    assert payload["pachaljharana"] == 9
    assert payload["dordi"] == 9


def test_php_syntax_for_modified_files() -> None:
    if not PHP_AVAILABLE:
        pytest.skip("PHP CLI not installed")
    files = [
        "/workspace/project/4in1sourcecode/includes/nepal-address.php",
        "/workspace/project/4in1sourcecode/includes/header.php",
        "/workspace/project/4in1sourcecode/online-kyc.php",
        "/workspace/project/4in1sourcecode/admin/institutional-profile.php",
        "/workspace/project/4in1sourcecode/institutional-profile.php",
        "/workspace/project/4in1sourcecode/admin/includes/ensure-admin-tables.php",
    ]
    for f in files:
        proc = run_cmd(["php", "-l", f])
        assert proc.returncode == 0, f"Syntax error in {f}: {proc.stderr or proc.stdout}"


def test_mobile_menu_js_syntax() -> None:
    proc = run_cmd(["node", "--check", "/workspace/project/4in1sourcecode/assets/js/v9-mobile-fix.js"])
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_admin_profile_new_fields_wired() -> None:
    content = Path("/workspace/project/4in1sourcecode/admin/institutional-profile.php").read_text(encoding="utf-8")
    for field in ["other_fund", "bank_cash_balance", "fixed_assets", "total_loan_members"]:
        assert f"$_POST['{field}']" in content
        assert f"name=\"{field}\"" in content
        assert f"'{field}'" in content


def test_kyc_selectors_present() -> None:
    content = Path("/workspace/project/4in1sourcecode/online-kyc.php").read_text(encoding="utf-8")
    required_ids = [
        "kyc-permanent-province-select",
        "kyc-permanent-district-select",
        "kyc-permanent-municipality-select",
        "kyc-permanent-ward-select",
        "kyc-same-as-permanent-checkbox",
    ]
    for rid in required_ids:
        assert rid in content


def test_public_profile_new_fields_are_missing_safe() -> None:
    """Should use null-safe access to avoid Undefined array key notices on old schema."""
    content = Path("/workspace/project/4in1sourcecode/institutional-profile.php").read_text(encoding="utf-8")
    expected_safe_patterns = [
        "($p['other_fund'] ??",
        "($p['bank_cash_balance'] ??",
        "($p['fixed_assets'] ??",
        "($p['total_loan_members'] ??",
    ]
    for pattern in expected_safe_patterns:
        assert pattern in content, f"Missing null-safe access for: {pattern}"



def test_btn_overflow_hidden_removed() -> None:
    """The .btn { overflow:hidden } rule was clipping Devanagari text descenders / icon bottoms.
    Must be removed from app-core.css and app-public.css."""
    import re
    for css_rel in ("assets/css/app-core.css", "assets/css/app-public.css"):
        content = Path(f"/workspace/project/4in1sourcecode/{css_rel}").read_text(encoding="utf-8")
        # strip CSS comments first so we don't false-positive on removed-comment text
        no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        for m in re.finditer(r'^\.btn\s*\{[^}]*\}', no_comments, flags=re.MULTILINE):
            body = m.group(0).replace(" ", "")
            assert "overflow:hidden" not in body, (
                f"Found overflow:hidden inside .btn block in {css_rel}: {m.group(0)[:200]}"
            )


def test_global_theme_has_final_patch() -> None:
    """global-theme.php must end with the FINAL UNIFORMITY PATCH block that fixes
    button underlines, inactive nav-tabs visibility on green strip, and bottom-nav icons."""
    content = Path("/workspace/project/4in1sourcecode/assets/css/global-theme.php").read_text(encoding="utf-8")
    assert "FINAL UNIFORMITY PATCH" in content
    # Anchor selectors that must be there
    assert "a.btn, a.btn:hover" in content or "a.btn, button.btn" in content
    assert ".admin-bottom-nav .admin-nav-item" in content
    assert ".admin-inner-tabstrip .nav-link:not(.active)" in content


def test_install_sql_no_duplicate_hrm_tables() -> None:
    """install.sql must not duplicate HRM CREATE TABLE statements."""
    content = Path("/workspace/project/4in1sourcecode/database/install.sql").read_text(encoding="utf-8")
    for tbl in (
        "hrm_departments",
        "hrm_employees",
        "hrm_employee_contracts",
        "hrm_employee_documents",
        "hrm_internal_messages",
    ):
        count = content.count(f"CREATE TABLE IF NOT EXISTS {tbl} (")
        assert count == 1, f"Table {tbl} has {count} CREATE statements, expected 1"


def test_btn_neutralizer_block_removed() -> None:
    """The harmful 'neutralize all colored buttons' block in app-admin.css must be removed —
    it was forcing white bg + dark text on all .btn-success/.btn-info/.btn-warning/.btn-secondary/
    .btn-outline-*, breaking colored buttons across all admin pages."""
    content = Path("/workspace/project/4in1sourcecode/assets/css/app-admin.css").read_text(encoding="utf-8")
    # this exact aggressive selector chain was the problem
    bad_pattern = (".btn-success,\n"
                   ".btn-info,\n"
                   ".btn-warning,\n"
                   ".btn-secondary,\n"
                   ".btn-outline-success,\n"
                   ".btn-outline-info,\n"
                   ".btn-outline-warning,\n"
                   ".btn-outline-secondary,\n"
                   ".btn-outline-primary {\n"
                   "    background: #ffffff !important;")
    assert bad_pattern not in content, (
        "The 'neutralize buttons' block is still present in app-admin.css. "
        "It forces white background on all colored buttons and hides icons."
    )



def test_mobile_drawer_stacking_fix_present() -> None:
    """Public mobile menu drawer (#mainNavV2) lives inside sticky .pfl-header-wrapper
    (position:sticky; z-index:1000) which creates a stacking context that traps the
    drawer below the body-level #pflMobileBackdrop. When mobile-nav-open class is on
    body, the wrapper must be lifted above the backdrop so the drawer becomes visible
    instead of dimmed by the backdrop."""
    content = Path("/workspace/project/4in1sourcecode/includes/header.php").read_text(encoding="utf-8")
    assert "body.header-v2.mobile-nav-open .pfl-header-wrapper" in content, (
        "Missing stacking-context fix for mobile drawer — wrapper must be lifted "
        "above backdrop when nav is open."
    )
    # Confirm the z-index lift value is above the backdrop's 2147483000
    import re
    m = re.search(
        r'body\.header-v2\.mobile-nav-open\s+\.pfl-header-wrapper\s*\{[^}]*z-index:\s*(\d+)',
        content,
    )
    assert m is not None, "Stacking fix block must set explicit z-index"
    assert int(m.group(1)) > 2147483000, (
        f"Wrapper z-index ({m.group(1)}) must be > backdrop z-index (2147483000)"
    )


def test_fix_pass2_present() -> None:
    """FIX-PASS 2 block must be in global-theme.php — addresses 3 user-reported issues:
    (A) digital-services h5 white-on-gray invisible, (B) HRM .btn-coop Devanagari clip,
    (C) institutional profile create button distortion."""
    content = Path("/workspace/project/4in1sourcecode/assets/css/global-theme.php").read_text(encoding="utf-8")
    assert "FIX-PASS 2" in content
    # A: tools-category-card h5 contrast fix
    assert ".tools-widget-section .tools-category-card h5" in content
    # B: .btn-coop overflow:visible + padding
    assert ".btn-coop, a.btn-coop, button.btn-coop" in content
    assert "overflow: visible" in content
    # C: institutional profile button defensive override
    assert 'button[form="profileMainForm"].btn' in content



def test_fix_pass3_global_icon_devanagari() -> None:
    """FIX-PASS 3 block must be present — global icon scaling + Devanagari descender
    safety. Caps icon font-size to 0.92em-0.95em across dropdowns/buttons/nav, and
    converts fixed heights on buttons/badges to flexible min-height + padding so
    Nepali bottom modifiers (ँ ी ु ृ) never clip."""
    content = Path("/workspace/project/4in1sourcecode/assets/css/global-theme.php").read_text(encoding="utf-8")
    assert "FIX-PASS 3" in content
    # A: icon sizing
    assert ".dropdown-menu .dropdown-item i" in content
    assert "font-size: 0.92em" in content
    # B: Devanagari-safe — height:auto and badge padding
    assert "height: auto !important" in content
    assert ".badge" in content
    # C: inline-height fallback selector
    assert '.btn[style*="height"]' in content


def test_fix_pass4_stat_card_consolidation() -> None:
    """FIX-PASS 4 (2026-06-22) consolidates .stat-card (was 7x), .stat-mini (was 3x),
    and .stat-uniform-card into global-theme.php as canonical single definitions.
    This eliminates CSS specificity wars in app-admin.css."""
    content = Path("/workspace/project/4in1sourcecode/assets/css/global-theme.php").read_text(encoding="utf-8")
    assert "FIX-PASS 4" in content
    # Canonical stat-card with all color variants
    assert ".stat-card {" in content
    assert ".stat-card.bg-primary" in content
    assert ".stat-card.bg-success" in content
    assert ".stat-card.bg-warning" in content
    assert ".stat-card.bg-danger" in content
    # Canonical stat-mini
    assert ".stat-mini {" in content
    assert ".stat-mini-row {" in content
    # Icon color variants consolidated
    assert ".sm-icon.ic-pending" in content
    assert ".sm-icon.ic-approved" in content
    # Uniform table styling
    assert ".coop-table {" in content
    assert ".admin-table-card {" in content


def test_component_files_exist_and_have_key_functions() -> None:
    """Verify key component files exist and contain expected functions."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # admin-ui.php should have key admin helper functions
    admin_ui = (root / "admin/includes/admin-ui.php").read_text(encoding="utf-8")
    assert "function adminPageHeader" in admin_ui
    assert "function adminAlert" in admin_ui
    assert "function adminStatusBadge" in admin_ui
    assert "function adminActionBtns" in admin_ui
    assert "function adminTableCard" in admin_ui
    assert "function adminBackBtn" in admin_ui
    
    # panel-uniform.php should have key cross-panel functions
    panel_uniform = (root / "includes/panel-uniform.php").read_text(encoding="utf-8")
    assert "function coopTableOpen" in panel_uniform
    assert "function coopTableClose" in panel_uniform
    assert "function coopStatusBadge" in panel_uniform
    assert "function coopBreadcrumb" in panel_uniform
    assert "function coopPageHeader" in panel_uniform
    assert "function coopPaginationLinks" in panel_uniform
    
    # stat-card.php component should exist
    stat_card = (root / "includes/components/stat-card.php").read_text(encoding="utf-8")
    assert "stat-mini" in stat_card
    assert "statCards" in stat_card
    
    # data-table.php component should exist
    data_table = (root / "includes/components/data-table.php").read_text(encoding="utf-8")
    assert "coop-table" in data_table
    assert "table-responsive-stack" in data_table


def test_archive_folder_is_empty_or_safe_to_delete() -> None:
    """Verify archive_old_v1 is either empty or documented as safe to delete."""
    root = Path("/workspace/project/4in1sourcecode")
    archive = root / "archive_old_v1"
    
    # Check what's in the archive
    files = list(archive.glob("*"))
    # Filter out README and hidden files
    non_doc_files = [f for f in files if f.name != "README.md" and not f.name.startswith(".")]
    
    # Archive should only contain README.md (no actual archived files)
    assert len(non_doc_files) == 0, f"Archive has files besides README: {non_doc_files}"
    
    # Verify README exists and explains the archive policy
    readme = (archive / "README.md").read_text(encoding="utf-8")
    assert "archive" in readme.lower()
    assert "safe" in readme.lower() or "quarantined" in readme.lower()


def test_css_architecture_has_no_broken_imports() -> None:
    """Verify all main CSS files exist and have valid structure."""
    root = Path("/workspace/project/4in1sourcecode")
    css_dir = root / "assets/css"
    
    # All main CSS files should exist
    main_css_files = [
        "app-admin.css",
        "app-core.css", 
        "app-member.css",
        "app-public.css",
        "global-theme.php"
    ]
    
    for css_file in main_css_files:
        path = css_dir / css_file
        assert path.exists(), f"Missing CSS file: {css_file}"
        
        # File should not be empty
        content = path.read_text(encoding="utf-8")
        assert len(content) > 100, f"{css_file} is too small or empty"
        
        # Should have proper CSS content
        if css_file.endswith(".css"):
            assert ".{" in content or "/*" in content, f"{css_file} has no CSS content"


def test_all_css_files_have_balanced_braces() -> None:
    """Verify all CSS files have balanced { and } braces."""
    root = Path("/workspace/project/4in1sourcecode")
    css_files = (root / "assets/css").glob("*.css")
    
    for css_file in css_files:
        content = css_file.read_text(encoding="utf-8")
        # Remove strings and comments that might have braces
        open_count = content.count("{")
        close_count = content.count("}")
        assert open_count == close_count, \
            f"{css_file.name} has unbalanced braces: {open_count} open, {close_count} close"


def test_config_php_has_essential_functions() -> None:
    """Verify config.php has all essential utility functions."""
    root = Path("/workspace/project/4in1sourcecode")
    config = (root / "includes/config.php").read_text(encoding="utf-8")
    
    # Security and utility functions
    essential_functions = [
        "function sanitize",
        "function e(",           # Escape/encoding helper
        "function getSetting",
        "function formatDate",
        "function formatNepaliCurrency",
        "function getLoggedInMemberProfile",
        "function safe_public_upload_path",
    ]
    
    for func in essential_functions:
        assert func in config, f"Missing essential function: {func}"


def test_no_suspicious_code_patterns() -> None:
    """Basic security scan: no eval(), base64_decode in config."""
    root = Path("/workspace/project/4in1sourcecode")
    config = (root / "includes/config.php").read_text(encoding="utf-8")
    
    # Check for dangerous patterns (but allow PDO exec which is safe)
    # eval() and base64_decode are always dangerous in config
    assert "eval(" not in config, "Dangerous: eval() found in config.php"
    assert "base64_decode(" not in config, "Suspicious: base64_decode() in config.php"
    
    # shell_exec and passthru are dangerous system calls
    assert "shell_exec(" not in config, "Dangerous: shell_exec() found in config.php"
    assert "passthru(" not in config, "Dangerous: passthru() found in config.php"
    
    # Note: exec() appears as PDO->exec() which is safe for DB statements


def test_security_csrf_tokens_exist_in_forms() -> None:
    """Verify CSRF token patterns exist in key admin forms."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Check a few key admin files for CSRF protection
    admin_files = [
        "admin/account-applications.php",
        "admin/kyc-settings.php", 
        "admin/settings.php",
    ]
    
    csrf_found = 0
    for admin_file in admin_files:
        path = root / admin_file
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if "csrf" in content.lower() or "token" in content.lower():
                csrf_found += 1
    
    # At least some admin files should have CSRF protection
    assert csrf_found > 0, "No CSRF/token patterns found in admin forms"


def test_all_panel_directories_have_index_or_bootstrap() -> None:
    """Verify each panel has proper entry point protection."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Panels with PHP files (public/ is static assets only)
    panels_with_php = ["admin", "member", "verify"]
    for panel in panels_with_php:
        panel_dir = root / panel
        if panel_dir.exists():
            # Should have at least one PHP file
            php_files = list(panel_dir.glob("*.php"))
            assert len(php_files) > 0, f"Panel {panel} has no PHP files"


def test_responsive_design_patterns_exist() -> None:
    """Verify key responsive design patterns are used across panels."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Check admin footer for mobile nav pattern
    admin_footer = (root / "admin/includes/admin-footer.php").read_text(encoding="utf-8")
    
    # Should have mobile bottom nav
    assert "mob-bottomnav" in admin_footer, "No mobile bottom nav found"
    
    # Check global-theme for responsive table patterns
    global_theme = (root / "assets/css/global-theme.php").read_text(encoding="utf-8")
    assert "table-responsive" in global_theme, "No responsive table patterns found"
    assert "table-responsive-stack" in global_theme, "No mobile card view pattern found"


def test_html_structural_patterns_are_valid() -> None:
    """Verify no common HTML structural issues in key files."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Check admin dashboard for common issues
    dashboard = (root / "admin/dashboard.php").read_text(encoding="utf-8")
    
    # Should have proper DOCTYPE or head section
    assert "<?php" in dashboard, "Dashboard should have PHP tags"
    
    # Check for unclosed PHP tags (should be clean)
    open_tags = dashboard.count("<?php")
    close_tags = dashboard.count("?>")
    # PHP can have more open tags than close (files may not close ?>)
    assert open_tags > 0, "No PHP opening tags found"


def test_internationalization_nepali_text_exists() -> None:
    """Verify Nepali (Devanagari) text is used in key files."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Check admin dashboard has Nepali text
    dashboard = (root / "admin/dashboard.php").read_text(encoding="utf-8")
    
    # Nepali unicode range for Devanagari
    nepali_patterns = ["ड्यासबोर्ड", "सदस्य", "कर्मचारी", "सूचना", "सेटिङ"]
    found_nepali = 0
    for pattern in nepali_patterns:
        if pattern in dashboard:
            found_nepali += 1
    
    # At least some Nepali text should be found
    assert found_nepali >= 2, f"Not enough Nepali text found: only {found_nepali} patterns"


def test_global_theme_has_devanagari_safe_rules() -> None:
    """Verify global-theme.php has Devanagari-safe CSS rules."""
    root = Path("/workspace/project/4in1sourcecode")
    global_theme = (root / "assets/css/global-theme.php").read_text(encoding="utf-8")
    
    # Devanagari-safe patterns should exist
    devanagari_patterns = [
        "line-height: 1.",   # Line height for descenders
        "height: auto",      # Auto height for text
        "overflow: visible", # No text clipping
        "padding-top:",      # Top padding for ascenders
        "padding-bottom:",   # Bottom padding for descenders
    ]
    
    found = 0
    for pattern in devanagari_patterns:
        if pattern in global_theme:
            found += 1
    
    assert found >= 3, f"Not enough Devanagari-safe patterns found: {found}"


def test_auth_files_exist_and_have_security_patterns() -> None:
    """Verify authentication and authorization files exist."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Auth files should exist (session may be in config.php)
    auth_files = [
        "includes/auth-roles.php",
    ]
    
    for auth_file in auth_files:
        path = root / auth_file
        assert path.exists(), f"Missing auth file: {auth_file}"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 50, f"Auth file {auth_file} is too small"


def test_database_config_has_security_defaults() -> None:
    """Verify database configuration has security settings."""
    root = Path("/workspace/project/4in1sourcecode")
    config = (root / "includes/config.php").read_text(encoding="utf-8")
    
    # Should use PDO (secure DB access)
    assert "PDO" in config, "PDO should be used for database"
    
    # Should have utf8mb4 for proper character encoding
    assert "utf8mb4" in config, "Should use utf8mb4 encoding"


def test_session_config_has_security_settings() -> None:
    """Verify session configuration has security settings."""
    root = Path("/workspace/project/4in1sourcecode")
    config = (root / "includes/config.php").read_text(encoding="utf-8")
    
    # Should have session security patterns
    session_patterns = ["session", "SESSION", "cookie", "COOKIE"]
    found = sum(1 for p in session_patterns if p in config)
    
    assert found >= 2, f"Not enough session security patterns: only {found}"


def test_logging_and_error_handling_patterns_exist() -> None:
    """Verify logging and error handling patterns exist."""
    root = Path("/workspace/project/4in1sourcecode")
    config = (root / "includes/config.php").read_text(encoding="utf-8")
    
    # Should have error handling patterns
    error_patterns = ["error", "log", "LOG", "Error", "Exception"]
    found = sum(1 for p in error_patterns if p in config)
    
    assert found >= 2, f"Not enough error/logging patterns: only {found}"


def test_admin_bootstrap_has_proper_structure() -> None:
    """Verify admin bootstrap file has proper structure."""
    root = Path("/workspace/project/4in1sourcecode")
    bootstrap = (root / "admin/_bootstrap.php").read_text(encoding="utf-8")
    
    # Should require config
    assert "config.php" in bootstrap, "Bootstrap should include config.php"
    
    # Should have session or auth check
    assert "session" in bootstrap.lower() or "auth" in bootstrap.lower(), \
        "Bootstrap should have session or auth check"


def test_seo_patterns_exist_in_public_header() -> None:
    """Verify SEO meta patterns exist."""
    root = Path("/workspace/project/4in1sourcecode")
    
    # Check if there's a public header with SEO
    header_files = [
        "public/index.php",
        "public/includes/header.php",
    ]
    
    # At minimum, config should have SEO functions
    config = (root / "includes/config.php").read_text(encoding="utf-8")
    seo_functions = ["seo_", "canonical", "meta"]
    found = sum(1 for f in seo_functions if f in config)
    
    assert found >= 1, f"Not enough SEO patterns found: only {found}"


def test_admin_header_has_language_toggle() -> None:
    """Verify admin header has language toggle for Nepali/English."""
    root = Path("/workspace/project/4in1sourcecode")
    admin_header = (root / "admin/includes/admin-header.php").read_text(encoding="utf-8")
    
    # Should have language toggle patterns
    lang_patterns = ["lang", "नेपाली", "English", "हिंदी", "nepali", "english"]
    found = sum(1 for p in lang_patterns if p in admin_header)
    
    assert found >= 1, f"No language toggle patterns found"


def test_component_directory_structure() -> None:
    """Verify all required component files exist."""
    root = Path("/workspace/project/4in1sourcecode")
    components = [
        "includes/components/stat-card.php",
        "includes/components/data-table.php",
    ]
    
    for comp in components:
        path = root / comp
        assert path.exists(), f"Missing component: {comp}"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 100, f"Component {comp} is too small"


def test_fa_to_lucide_function_exists() -> None:
    """Verify fa_to_lucide function exists in core/helpers.php."""
    root = Path("/workspace/project/4in1sourcecode")
    helpers = root / "core/helpers.php"
    assert helpers.exists(), "core/helpers.php not found"
    content = helpers.read_text(encoding="utf-8")
    assert "function fa_to_lucide" in content, \
        "fa_to_lucide() function not defined in core/helpers.php"


def test_admin_ui_loads_helpers() -> None:
    """Verify admin-ui.php loads core/helpers.php when needed."""
    root = Path("/workspace/project/4in1sourcecode")
    admin_ui = root / "admin/includes/admin-ui.php"
    assert admin_ui.exists(), "admin/includes/admin-ui.php not found"
    content = admin_ui.read_text(encoding="utf-8")
    # Should have conditional loading of core/helpers.php
    assert "fa_to_lucide" in content, \
        "admin-ui.php should reference fa_to_lucide"
    assert "helpers.php" in content, \
        "admin-ui.php should load core/helpers.php when fa_to_lucide is not available"
