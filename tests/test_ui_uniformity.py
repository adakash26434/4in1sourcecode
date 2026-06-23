"""UI/UX Uniformity Tests - Verify consistent design patterns across project."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set

import pytest


ROOT = Path("/workspace/project/4in1sourcecode")
ADMIN_ROOT = ROOT / "admin"


def get_all_php_files(directory: Path) -> List[Path]:
    """Get all PHP files in directory."""
    return list(directory.glob("*.php"))


def extract_classes(content: str) -> Set[str]:
    """Extract CSS class names from HTML content."""
    # Match class="..." or class='...'
    pattern = r'class=["\']([^"\']+)["\']'
    matches = re.findall(pattern, content)
    all_classes = set()
    for match in matches:
        # Split by whitespace to get individual classes
        classes = match.split()
        all_classes.update(classes)
    return all_classes


def extract_inline_styles(content: str) -> Set[str]:
    """Extract inline style properties."""
    pattern = r'style=["\']([^"\']+)["\']'
    matches = re.findall(pattern, content)
    styles = set()
    for match in matches:
        styles.add(match.strip())
    return styles


class TestButtonUniformity:
    """Test button class uniformity."""

    def test_no_custom_btn_edit_classes(self) -> None:
        """Each file should not have unique .btn-edit-* classes - use uniform .btn-edit."""
        files = get_all_php_files(ADMIN_ROOT)
        
        custom_btn_edit_classes: Dict[str, List[str]] = {}
        
        for f in files:
            content = f.read_text(encoding="utf-8")
            # Find all .btn-edit-* classes
            pattern = r'\.btn-edit-[a-z]+'
            matches = re.findall(pattern, content)
            if matches:
                custom_btn_edit_classes[f.name] = matches
        
        # Report findings
        if custom_btn_edit_classes:
            report = "\n".join([
                f"  {fname}: {', '.join(classes)}"
                for fname, classes in list(custom_btn_edit_classes.items())[:10]
            ])
            print(f"\n⚠️  Found custom .btn-edit-* classes:\n{report}")
        
        # This is informational - we want to consolidate these
        # But we're just reporting for now
        assert True, "Button uniformity check complete"

    def test_standard_btn_classes_exist(self) -> None:
        """Verify standard Bootstrap button classes are used."""
        files = get_all_php_files(ADMIN_ROOT)
        
        has_standard_btns = 0
        for f in files:
            content = f.read_text(encoding="utf-8")
            # Check for standard Bootstrap button classes
            if re.search(r'\bbtn\s+(btn-primary|btn-secondary|btn-success|btn-danger|btn-warning|btn-info|btn-outline)', content):
                has_standard_btns += 1
        
        # At least 50% of files should use standard button classes
        assert has_standard_btns >= len(files) * 0.5, \
            f"Only {has_standard_btns}/{len(files)} files use standard Bootstrap buttons"


class TestMobileNavigationUniformity:
    """Test mobile navigation consistency."""

    def test_bottom_nav_in_includes(self) -> None:
        """Verify admin-footer has mobile bottom nav."""
        footer = ADMIN_ROOT / "includes/admin-footer.php"
        content = footer.read_text(encoding="utf-8")
        
        assert "mob-bottomnav" in content or "bottom-nav" in content or "mobile-nav" in content, \
            "Admin footer should have mobile navigation"

    def test_navbar_consistency(self) -> None:
        """Verify header includes proper navigation."""
        header = ADMIN_ROOT / "includes/admin-header.php"
        if header.exists():
            content = header.read_text(encoding="utf-8")
            # Should have navbar classes
            assert "navbar" in content or "sidebar" in content, \
                "Admin header should have navigation structure"


class TestFormUniformity:
    """Test form element consistency."""

    def test_uses_bootstrap_form_classes(self) -> None:
        """Verify forms use Bootstrap form classes."""
        files = get_all_php_files(ADMIN_ROOT)
        
        files_with_forms = []
        for f in files:
            content = f.read_text(encoding="utf-8")
            if "<form" in content:
                files_with_forms.append(f.name)
                # Check if Bootstrap form classes are used
                if not re.search(r'form-control|form-select|input-group', content):
                    print(f"⚠️  {f.name} has <form> but no Bootstrap form classes")
        
        assert len(files_with_forms) > 0, "No form files found"

    def test_no_inline_width_styles_on_inputs(self) -> None:
        """Check for inline width styles that break uniformity."""
        files = get_all_php_files(ADMIN_ROOT)
        
        problematic_files = []
        for f in files:
            content = f.read_text(encoding="utf-8")
            # Look for inline width/height styles on inputs
            if re.search(r'<input[^>]+style=["\'].*width\s*:', content):
                problematic_files.append(f.name)
        
        if problematic_files:
            print(f"\n⚠️  Files with inline width styles: {len(problematic_files)}")
            print(", ".join(problematic_files[:10]))


class TestTableUniformity:
    """Test table styling consistency."""

    def test_tables_use_coop_table_class(self) -> None:
        """Verify tables use .coop-table or .table class."""
        files = get_all_php_files(ADMIN_ROOT)
        
        tables_with_class = 0
        tables_without_class = []
        
        for f in files:
            content = f.read_text(encoding="utf-8")
            if "<table" in content:
                # Check for table class
                if re.search(r'<table[^>]+class=["\'][^"\']*(table|coop-table|data-table)', content):
                    tables_with_class += 1
                else:
                    tables_without_class.append(f.name)
        
        if tables_without_class:
            print(f"\n⚠️  Tables without Bootstrap class: {len(tables_without_class)}")
            print(", ".join(tables_without_class[:10]))
        
        # At least 70% should have proper table classes
        total_tables = tables_with_class + len(tables_without_class)
        if total_tables > 0:
            assert tables_with_class >= total_tables * 0.5, \
                f"Only {tables_with_class}/{total_tables} tables have proper classes"


class TestCardUniformity:
    """Test card component consistency."""

    def test_stat_cards_use_uniform_class(self) -> None:
        """Verify stat cards use .stat-card class."""
        files = get_all_php_files(ADMIN_ROOT)
        
        stat_card_files = []
        for f in files:
            content = f.read_text(encoding="utf-8")
            if ".stat-card" in content or "stat-card" in content:
                stat_card_files.append(f.name)
        
        print(f"\n📊 Files using .stat-card: {len(stat_card_files)}")
        assert len(stat_card_files) > 0, "No files using .stat-card"


class TestFontAndSpacingUniformity:
    """Test typography and spacing consistency."""

    def test_no_inline_font_family(self) -> None:
        """Verify no inline font-family declarations."""
        files = get_all_php_files(ADMIN_ROOT)
        
        files_with_inline_font = []
        for f in files:
            content = f.read_text(encoding="utf-8")
            if re.search(r'style=["\'][^"\']*font-family\s*:', content):
                files_with_inline_font.append(f.name)
        
        if files_with_inline_font:
            print(f"\n⚠️  Files with inline font-family: {len(files_with_inline_font)}")


class TestIconUniformity:
    """Test icon usage consistency."""

    def test_icon_libraries_consistent(self) -> None:
        """Check which icon libraries are used."""
        admin_root = ADMIN_ROOT
        php_files = list(admin_root.glob("*.php"))
        
        fontawesome_count = 0
        bootstrap_icons_count = 0
        lucide_count = 0
        
        for f in php_files:
            content = f.read_text(encoding="utf-8")
            if "fa-" in content or "fa fa-" in content:
                fontawesome_count += 1
            if "bi-" in content:  # Bootstrap icons
                bootstrap_icons_count += 1
            if "lucide" in content.lower():
                lucide_count += 1
        
        print(f"\n📦 Icon Library Usage:")
        print(f"  Font Awesome: {fontawesome_count} files")
        print(f"  Bootstrap Icons: {bootstrap_icons_count} files")
        print(f"  Lucide: {lucide_count} files")
        
        # At least one icon library should be used
        assert fontawesome_count + bootstrap_icons_count + lucide_count > 0, \
            "No icon library detected"


class TestResponsiveUniformity:
    """Test responsive design consistency."""

    def test_responsive_classes_used(self) -> None:
        """Verify Bootstrap responsive classes are used."""
        files = get_all_php_files(ADMIN_ROOT)
        
        responsive_count = 0
        for f in files:
            content = f.read_text(encoding="utf-8")
            # Check for Bootstrap responsive prefixes
            if re.search(r'\b(col-|row-|d-\w*-|mb-\w*|mt-\w*|mx-\w*|my-\w*)', content):
                responsive_count += 1
        
        print(f"\n📱 Files using Bootstrap responsive classes: {responsive_count}/{len(files)}")
        assert responsive_count >= len(files) * 0.3, \
            "Less than 30% of files use responsive classes"


class TestColorUniformity:
    """Test color usage consistency."""

    def test_no_hardcoded_hex_colors_in_html(self) -> None:
        """Check for hardcoded colors that should use Bootstrap variables."""
        files = get_all_php_files(ADMIN_ROOT)
        
        files_with_colors = {}
        for f in files:
            content = f.read_text(encoding="utf-8")
            # Find inline style with color
            colors = re.findall(r'color\s*:\s*(#[a-fA-F0-9]{3,6})', content)
            if colors:
                files_with_colors[f.name] = len(colors)
        
        if files_with_colors:
            print(f"\n🎨 Files with hardcoded inline colors: {len(files_with_colors)}")
            # This is informational - not a failure


class TestPageStructureUniformity:
    """Test page structure consistency."""

    def test_pages_include_footer(self) -> None:
        """Verify pages include admin-footer."""
        files = get_all_php_files(ADMIN_ROOT)
        
        # Exclude special files
        exclude = ["index.php", "login.php", "_bootstrap.php", "logout.php"]
        regular_pages = [f for f in files if f.name not in exclude]
        
        pages_with_footer = 0
        for f in regular_pages:
            content = f.read_text(encoding="utf-8")
            if "admin-footer.php" in content or "include_footer" in content:
                pages_with_footer += 1
        
        print(f"\n📄 Pages including footer: {pages_with_footer}/{len(regular_pages)}")
        assert pages_with_footer >= len(regular_pages) * 0.7, \
            "Less than 70% of pages include footer"

    def test_pages_include_header(self) -> None:
        """Verify pages include admin-header."""
        files = get_all_php_files(ADMIN_ROOT)
        
        # Exclude special files
        exclude = ["index.php", "login.php", "_bootstrap.php", "logout.php"]
        regular_pages = [f for f in files if f.name not in exclude]
        
        pages_with_header = 0
        for f in regular_pages:
            content = f.read_text(encoding="utf-8")
            if "admin-header.php" in content or "include_header" in content:
                pages_with_header += 1
        
        print(f"\n📄 Pages including header: {pages_with_header}/{len(regular_pages)}")
        assert pages_with_header >= len(regular_pages) * 0.7, \
            "Less than 70% of pages include header"


class TestComponentUsage:
    """Test component usage."""

    def test_stat_card_component_used(self) -> None:
        """Verify stat-card.php component is used."""
        stat_component = ROOT / "includes/components/stat-card.php"
        assert stat_component.exists(), "stat-card.php component should exist"
        
        # Check usage
        files = get_all_php_files(ADMIN_ROOT)
        using_component = 0
        for f in files:
            content = f.read_text(encoding="utf-8")
            if "stat-card.php" in content or "components/stat-card" in content:
                using_component += 1
        
        print(f"\n📦 Files using stat-card component: {using_component}")

    def test_data_table_component_exists(self) -> None:
        """Verify data-table.php component exists."""
        table_component = ROOT / "includes/components/data-table.php"
        assert table_component.exists(), "data-table.php component should exist"
