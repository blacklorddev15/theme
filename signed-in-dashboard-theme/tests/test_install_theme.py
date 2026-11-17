from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THEME = Path(__file__).resolve().parents[1]
INSTALLER = THEME / "install-theme.py"
VERSION = "2026.11.17.1"

PROVIDER = r'''<?php
namespace Pterodactyl\Providers;
use Illuminate\Database\QueryException;
use Illuminate\Contracts\Config\Repository as ConfigRepository;
use Illuminate\Contracts\Encryption\Encrypter;
use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;
class SettingsServiceProvider
{
    /**
     * Boot the service provider.
     */
    public function boot(ConfigRepository $config, Encrypter $encrypter, Log $log, SettingsRepositoryInterface $settings): void
    {
        // Only set the email driver settings from the database if we
        // are configured using SMTP as the driver.
        if ($config->get('mail.default') === 'smtp') {
            // existing mail settings logic
        }
    }
}
'''


class ThemeInstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="blacklord-theme-test-")
        self.base = Path(self.temporary.name)
        self.panel = self.base / "panel"
        self.backups = self.base / "private-backups"
        self.make_panel()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_panel(self) -> None:
        (self.panel / "app/Providers").mkdir(parents=True)
        (self.panel / "app/Http/Controllers/Admin").mkdir(parents=True)
        (self.panel / "public/assets").mkdir(parents=True)
        (self.panel / "routes").mkdir(parents=True)
        (self.panel / "resources/views/layouts").mkdir(parents=True)
        (self.panel / "resources/views/templates/auth").mkdir(parents=True)
        (self.panel / "resources/views/templates").mkdir(parents=True, exist_ok=True)
        (self.panel / "resources/views/admin").mkdir(parents=True)
        (self.panel / "artisan").write_text("#!/usr/bin/env php\n<?php\n", encoding="utf-8")
        (self.panel / "app/Providers/SettingsServiceProvider.php").write_text(PROVIDER, encoding="utf-8")
        (self.panel / "routes/admin.php").write_text("<?php\n// Existing admin routes.\n", encoding="utf-8")
        (self.panel / "resources/views/layouts/admin.blade.php").write_text(
            '<!doctype html><html><head>\n</head><body>\n'
            '<li class="settings">Settings</li>\n'
            '<li class="header">MANAGEMENT</li>\n'
            '</body></html>\n', encoding="utf-8"
        )
        (self.panel / "resources/views/templates/base").mkdir(parents=True)
        (self.panel / "resources/views/templates/base/core.blade.php").write_text(
            "@extends('templates/wrapper')\n@section('assets')\n"
            '<link rel="stylesheet" href="/assets/login-only.css">\n'
            "@endsection\n@section('container')\n<div>Signed in</div>\n@endsection\n",
            encoding="utf-8",
        )
        self.login_file = self.panel / "resources/views/templates/auth/core.blade.php"
        self.login_original = "LOGIN TEMPLATE MUST REMAIN BYTE-FOR-BYTE UNCHANGED\n"
        self.login_file.write_text(self.login_original, encoding="utf-8")

    def run_installer(self, extra_env: dict[str, str] | None = None, package: Path = THEME) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["BLACKLORD_THEME_BACKUP_ROOT"] = str(self.backups)
        env["BLACKLORD_THEME_SKIP_ARTISAN"] = "1"
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [sys.executable, str(INSTALLER), str(self.panel), str(package), VERSION],
            check=False, capture_output=True, text=True, env=env, timeout=30,
        )

    def test_install_adds_signed_in_theme_editor_and_preserves_login(self) -> None:
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.panel / "public/assets/james-signed-in.css").is_file())
        self.assertTrue((self.panel / "public/assets/james-store-background.jpg").is_file())
        self.assertIn("name('admin.theme')", (self.panel / "routes/admin.php").read_text())
        self.assertIn("Theme &amp; Branding", (self.panel / "resources/views/layouts/admin.blade.php").read_text())
        self.assertIn("/assets/james-admin.css?v=" + VERSION, (self.panel / "resources/views/layouts/admin.blade.php").read_text())
        client = (self.panel / "resources/views/templates/base/core.blade.php").read_text()
        self.assertIn("@auth", client)
        self.assertIn("/assets/james-signed-in.css?v=" + VERSION, client)
        self.assertIn("/assets/login-only.css", client)
        self.assertIn("Company Name", (self.panel / "resources/views/admin/panel-theme.blade.php").read_text())
        self.assertIn('"backgroundUrl": ""', (self.panel / "public/panel-theme.json").read_text())
        self.assertIn("BLACKLORD_THEME_MANAGED", (self.panel / "app/Http/Controllers/Admin/PanelThemeController.php").read_text())
        self.assertEqual(self.login_file.read_text(), self.login_original)
        manifests = list(self.backups.glob("*/manifest.json"))
        self.assertEqual(len(manifests), 1)
        backup_manifest = json.loads(manifests[0].read_text())
        self.assertIn("resources/views/templates/base/core.blade.php", [item["path"] for item in backup_manifest["files"]])

    def test_reinstall_is_idempotent_and_keeps_existing_company_theme_settings(self) -> None:
        first = self.run_installer()
        self.assertEqual(first.returncode, 0, first.stderr)
        config_path = self.panel / "public/panel-theme.json"
        custom_settings = '{"primaryColor":"#aabbcc","secondaryColor":"#ddeeff","backgroundUrl":"https://example.test/custom.jpg"}\n'
        config_path.write_text(custom_settings, encoding="utf-8")
        second = self.run_installer()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(config_path.read_text(), custom_settings)
        admin = (self.panel / "resources/views/layouts/admin.blade.php").read_text()
        client = (self.panel / "resources/views/templates/base/core.blade.php").read_text()
        self.assertEqual(admin.count("/assets/james-admin.css"), 1)
        self.assertEqual(client.count("/assets/james-signed-in.css"), 1)
        self.assertEqual((self.panel / "routes/admin.php").read_text().count("name('admin.theme')"), 1)
        self.assertEqual(self.login_file.read_text(), self.login_original)

    def test_unsupported_admin_layout_fails_before_any_change(self) -> None:
        bad_layout = self.panel / "resources/views/layouts/admin.blade.php"
        bad_layout.write_text("<html><head></head><body>Unknown layout</body></html>\n", encoding="utf-8")
        original_routes = (self.panel / "routes/admin.php").read_bytes()
        original_provider = (self.panel / "app/Providers/SettingsServiceProvider.php").read_bytes()
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.panel / "public/assets/james-admin.css").exists())
        self.assertEqual((self.panel / "routes/admin.php").read_bytes(), original_routes)
        self.assertEqual((self.panel / "app/Providers/SettingsServiceProvider.php").read_bytes(), original_provider)
        self.assertEqual(list(self.backups.glob("*/manifest.json")), [])
        self.assertEqual(self.login_file.read_text(), self.login_original)

    def test_invalid_theme_package_fails_before_panel_changes(self) -> None:
        package_copy = self.base / "tampered-theme"
        shutil.copytree(THEME, package_copy, ignore=shutil.ignore_patterns("__pycache__"))
        (package_copy / "assets/james-admin.css").write_bytes(b"tampered-for-test")
        result = self.run_installer(package=package_copy)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.panel / "public/assets/james-admin.css").exists())
        self.assertEqual(self.login_file.read_text(), self.login_original)


if __name__ == "__main__":
    unittest.main()
