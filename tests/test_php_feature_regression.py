"""Regression checks for Nepal address dataset, KYC selectors, mobile JS, and profile fields."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path("/app")


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def run_php_inline(code: str) -> str:
    proc = run_cmd(["php", "-r", code])
    assert proc.returncode == 0, f"PHP failed: {proc.stderr or proc.stdout}"
    return proc.stdout.strip()


def test_nepal_address_counts_and_uniqueness() -> None:
    code = r'''
require '/app/includes/nepal-address.php';
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
require '/app/includes/nepal-address.php';
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
    files = [
        "/app/includes/nepal-address.php",
        "/app/includes/header.php",
        "/app/online-kyc.php",
        "/app/admin/institutional-profile.php",
        "/app/institutional-profile.php",
        "/app/admin/includes/ensure-admin-tables.php",
    ]
    for f in files:
        proc = run_cmd(["php", "-l", f])
        assert proc.returncode == 0, f"Syntax error in {f}: {proc.stderr or proc.stdout}"


def test_mobile_menu_js_syntax() -> None:
    proc = run_cmd(["node", "--check", "/app/assets/js/v9-mobile-fix.js"])
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_admin_profile_new_fields_wired() -> None:
    content = Path("/app/admin/institutional-profile.php").read_text(encoding="utf-8")
    for field in ["other_fund", "bank_cash_balance", "fixed_assets", "total_loan_members"]:
        assert f"$_POST['{field}']" in content
        assert f"name=\"{field}\"" in content
        assert f"'{field}'" in content


def test_kyc_selectors_present() -> None:
    content = Path("/app/online-kyc.php").read_text(encoding="utf-8")
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
    content = Path("/app/institutional-profile.php").read_text(encoding="utf-8")
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
        content = Path(f"/app/{css_rel}").read_text(encoding="utf-8")
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
    content = Path("/app/assets/css/global-theme.php").read_text(encoding="utf-8")
    assert "FINAL UNIFORMITY PATCH" in content
    # Anchor selectors that must be there
    assert "a.btn, a.btn:hover" in content or "a.btn, button.btn" in content
    assert ".admin-bottom-nav .admin-nav-item" in content
    assert ".admin-inner-tabstrip .nav-link:not(.active)" in content


def test_install_sql_no_duplicate_hrm_tables() -> None:
    """install.sql must not duplicate HRM CREATE TABLE statements."""
    content = Path("/app/database/install.sql").read_text(encoding="utf-8")
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
    content = Path("/app/assets/css/app-admin.css").read_text(encoding="utf-8")
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
