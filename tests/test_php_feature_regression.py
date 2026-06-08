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
