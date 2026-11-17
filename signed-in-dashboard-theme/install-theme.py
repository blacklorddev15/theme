#!/usr/bin/env python3
"""Install the Blacklord signed-in Pterodactyl theme with a reversible backup."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

THEME_NAME = "Blacklord Signed-in Theme"
REPOSITORY = "blacklorddev15/theme"
ALLOWED_FILES = {
    "install-theme.py",
    "assets/james-admin.css",
    "assets/james-signed-in.css",
    "assets/james-store-background.jpg",
    "assets/panel-theme.css",
    "assets/panel-theme.js",
    "panel/PanelThemeController.php",
    "panel/panel-theme.blade.php",
    "patches/company-name-only-settings-provider.patch",
}
TARGETS = {
    "assets/james-admin.css": "public/assets/james-admin.css",
    "assets/james-signed-in.css": "public/assets/james-signed-in.css",
    "assets/james-store-background.jpg": "public/assets/james-store-background.jpg",
    "assets/panel-theme.css": "public/assets/panel-theme.css",
    "assets/panel-theme.js": "public/assets/panel-theme.js",
    "panel/PanelThemeController.php": "app/Http/Controllers/Admin/PanelThemeController.php",
    "panel/panel-theme.blade.php": "resources/views/admin/panel-theme.blade.php",
}
PROVIDER_REL = "app/Providers/SettingsServiceProvider.php"
ROUTES_REL = "routes/admin.php"
ADMIN_LAYOUT_REL = "resources/views/layouts/admin.blade.php"
CLIENT_LAYOUT_REL = "resources/views/templates/base/core.blade.php"
CONFIG_REL = "public/panel-theme.json"
PROVIDER_PATCH_REL = "patches/company-name-only-settings-provider.patch"


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_and_verify_package(package: Path, expected_version: str) -> tuple[dict, dict[str, bytes]]:
    manifest_path = package / "manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        fail("theme manifest is missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("theme manifest is invalid")
    if manifest.get("name") != THEME_NAME or manifest.get("repository") != REPOSITORY:
        fail("theme manifest does not identify the expected repository")
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,32}", version):
        fail("theme version is invalid")
    if version != expected_version:
        fail("theme version does not match the downloaded package")
    entries = manifest.get("files")
    if not isinstance(entries, dict) or set(entries) != ALLOWED_FILES:
        fail("theme package file list is incomplete or contains unexpected files")

    files: dict[str, bytes] = {}
    total_size = 0
    for relative, metadata in entries.items():
        if not isinstance(relative, str) or relative not in ALLOWED_FILES:
            fail("theme package contains an invalid file path")
        if not isinstance(metadata, dict):
            fail("theme package metadata is invalid")
        expected_hash = metadata.get("sha256")
        expected_size = metadata.get("size")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_hash):
            fail("theme package hash is invalid")
        if not isinstance(expected_size, int) or expected_size < 0 or expected_size > 6 * 1024 * 1024:
            fail("theme package file size is invalid")
        source = package / relative
        if source.is_symlink() or not source.is_file():
            fail("a theme package file is missing")
        resolved = source.resolve(strict=True)
        if package.resolve(strict=True) not in resolved.parents:
            fail("theme package path escapes its source directory")
        data = source.read_bytes()
        if len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_hash:
            fail("theme package integrity check failed")
        total_size += len(data)
        if total_size > 10 * 1024 * 1024:
            fail("theme package is larger than allowed")
        files[relative] = data
    return manifest, files


def safe_panel_root(raw: str) -> Path:
    if not isinstance(raw, str) or not raw.startswith("/") or "\x00" in raw:
        fail("Panel root must be an absolute path")
    parts = Path(raw).parts
    if len(parts) < 3 or any(part in (".", "..") for part in parts):
        fail("Panel root path is not allowed")
    try:
        root = Path(raw).resolve(strict=True)
    except Exception:
        fail("Panel root does not exist")
    if root == Path("/") or not root.is_dir() or not (root / "artisan").is_file():
        fail("Panel root does not look like a Pterodactyl installation")
    return root


def checked_target(root: Path, relative: str) -> Path:
    if relative.startswith("/") or ".." in Path(relative).parts:
        fail("installer target path is invalid")
    target = root / relative
    if target.is_symlink():
        fail("refusing to replace a symlinked theme target")
    parent = target.parent.resolve(strict=True)
    if parent != root and root not in parent.parents:
        fail("installer target escapes the Panel directory")
    return target


def text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        fail("a required Panel source file could not be read")


def update_asset_urls(content: str, names: tuple[str, ...], version: str) -> tuple[str, list[str]]:
    missing: list[str] = []
    for name in names:
        escaped = re.escape(name)
        pattern = re.compile(rf"(/assets/{escaped})(?:\?v=[A-Za-z0-9._-]*)?(?=[\"'])")
        content = pattern.sub(rf"\1?v={version}", content)
        if not re.search(rf"/assets/{escaped}(?:\?[^\"']*)?[\"']", content):
            missing.append(name)
    return content, missing


def patch_provider(provider_text: str, patch_bytes: bytes, root: Path) -> bytes:
    marker = "In environment-only mode, load only the Company Name from the database."
    if marker in provider_text or (
        "pterodactyl.load_environment_only" in provider_text and
        "settings::app:name" in provider_text and
        "config->set('app.name', $value)" in provider_text
    ):
        return provider_text.encode("utf-8")
    if "use Illuminate\\Database\\QueryException;" not in provider_text:
        fail("Panel SettingsServiceProvider is not compatible with the Company Name patch")

    with tempfile.TemporaryDirectory(prefix="blacklord-theme-patch-") as temporary:
        stage = Path(temporary)
        staged_provider = stage / PROVIDER_REL
        staged_provider.parent.mkdir(parents=True)
        staged_provider.write_text(provider_text, encoding="utf-8")
        patch_file = stage / "company-name.patch"
        patch_file.write_bytes(patch_bytes)
        try:
            result = subprocess.run(
                ["patch", "--batch", "--forward", "--silent", "-p1", "-i", str(patch_file)],
                cwd=stage,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
            )
        except Exception:
            fail("the Company Name patch tool is unavailable")
        if result.returncode != 0:
            fail("Panel SettingsServiceProvider did not match the supported patch context")
        return staged_provider.read_bytes()


def make_admin_links(content: str, version: str) -> str:
    content, missing = update_asset_urls(content, ("james-admin.css", "panel-theme.css", "panel-theme.js"), version)
    if missing:
        tags = []
        if "james-admin.css" in missing:
            tags.append(f'        <link rel="stylesheet" href="/assets/james-admin.css?v={version}">')
        protected = [name for name in missing if name in ("panel-theme.css", "panel-theme.js")]
        if protected:
            tags.append("        @auth")
            if "panel-theme.css" in protected:
                tags.append(f'            <link rel="stylesheet" href="/assets/panel-theme.css?v={version}">')
            if "panel-theme.js" in protected:
                tags.append(f'            <script defer src="/assets/panel-theme.js?v={version}"></script>')
            tags.append("        @endauth")
        anchor = "</head>"
        if content.count(anchor) != 1:
            fail("Admin layout does not have one safe head insertion point")
        insertion = "\n        <!-- Blacklord signed-in theme assets -->\n" + "\n".join(tags) + "\n    "
        content = content.replace(anchor, insertion + anchor, 1)
    return content


def make_client_links(content: str, version: str) -> str:
    matches = list(re.finditer(r"@section\(['\"]assets['\"]\)(.*?)@endsection", content, re.S))
    if len(matches) != 1:
        fail("client layout does not have one safe signed-in asset section")
    match = matches[0]
    section = match.group(1)
    section, missing = update_asset_urls(section, ("james-signed-in.css", "panel-theme.css", "panel-theme.js"), version)
    if missing:
        tags = ["    @auth"]
        if "james-signed-in.css" in missing:
            tags.append(f'        <link rel="stylesheet" href="/assets/james-signed-in.css?v={version}">')
        if "panel-theme.css" in missing:
            tags.append(f'        <link rel="stylesheet" href="/assets/panel-theme.css?v={version}">')
        if "panel-theme.js" in missing:
            tags.append(f'        <script defer src="/assets/panel-theme.js?v={version}"></script>')
        tags.append("    @endauth\n")
        section += "\n" + "\n".join(tags)
    updated = content[:match.start(1)] + section + content[match.end(1):]
    if "templates/auth/core.blade.php" in updated:
        fail("authentication layout must not be modified")
    return updated


def prepare_plan(root: Path, package: Path, version: str, files: dict[str, bytes]) -> dict[Path, bytes]:
    plan: dict[Path, bytes] = {}
    for source_rel, target_rel in TARGETS.items():
        target = checked_target(root, target_rel)
        data = files[source_rel]
        if source_rel == "panel/PanelThemeController.php":
            if not data.startswith(b"<?php"):
                fail("theme controller source is invalid")
            data = data.replace(b"<?php", b"<?php\n/* BLACKLORD_THEME_MANAGED */", 1)
            if target.exists():
                current = target.read_bytes()
                if b"BLACKLORD_THEME_MANAGED" not in current and not (
                    b"class PanelThemeController" in current and b"settings::app:name" in current
                ):
                    fail("an unrecognized PanelThemeController already exists; refusing to overwrite it")
        elif source_rel == "panel/panel-theme.blade.php":
            data = b"{{-- BLACKLORD_THEME_MANAGED --}}\n" + data
            if target.exists():
                current = target.read_bytes()
                if b"BLACKLORD_THEME_MANAGED" not in current and not (
                    b"Theme &amp; Branding" in current and b'name="company_name"' in current
                ):
                    fail("an unrecognized theme editor view already exists; refusing to overwrite it")
        plan[target] = data

    provider = checked_target(root, PROVIDER_REL)
    provider_data = patch_provider(text_file(provider), files[PROVIDER_PATCH_REL], root)
    if provider_data != provider.read_bytes():
        plan[provider] = provider_data

    routes = checked_target(root, ROUTES_REL)
    routes_text = text_file(routes)
    if "name('admin.theme')" not in routes_text and 'name("admin.theme")' not in routes_text:
        routes_text = routes_text.rstrip() + "\n\n// Blacklord Theme & Branding editor routes.\n" \
            "Route::get('/theme', [\\Pterodactyl\\Http\\Controllers\\Admin\\PanelThemeController::class, 'index'])->name('admin.theme');\n" \
            "Route::post('/theme', [\\Pterodactyl\\Http\\Controllers\\Admin\\PanelThemeController::class, 'update'])->name('admin.theme.update');\n"
    plan[routes] = routes_text.encode("utf-8")

    admin_layout = checked_target(root, ADMIN_LAYOUT_REL)
    admin_text = text_file(admin_layout)
    if "route('admin.theme')" not in admin_text:
        anchor = '<li class="header">MANAGEMENT</li>'
        if admin_text.count(anchor) != 1:
            fail("Admin sidebar does not have one safe theme-link insertion point")
        link = '''<li class="{{ Route::currentRouteName() !== 'admin.theme' ?: 'active' }}">\n                            <a href="{{ route('admin.theme') }}">\n                                <i class="fa fa-paint-brush"></i> <span>Theme &amp; Branding</span>\n                            </a>\n                        </li>\n                        '''
        admin_text = admin_text.replace(anchor, link + anchor, 1)
    admin_text = make_admin_links(admin_text, version)
    plan[admin_layout] = admin_text.encode("utf-8")

    client_layout = checked_target(root, CLIENT_LAYOUT_REL)
    client_text = make_client_links(text_file(client_layout), version)
    plan[client_layout] = client_text.encode("utf-8")

    config = checked_target(root, CONFIG_REL)
    if not config.exists():
        plan[config] = b'{\n  "primaryColor": "#ffff00",\n  "secondaryColor": "#00ff00",\n  "backgroundUrl": ""\n}\n'
    return plan


def copy_metadata(path: Path, default_mode: int = 0o644) -> tuple[int, int, int]:
    if path.exists():
        info = path.stat()
        return info.st_mode, info.st_uid, info.st_gid
    info = path.parent.stat()
    return default_mode, info.st_uid, info.st_gid


def atomic_write(path: Path, data: bytes, metadata: tuple[int, int, int] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode, uid, gid = metadata or copy_metadata(path)
    fd, temporary = tempfile.mkstemp(prefix=".blacklord-theme-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, stat.S_IMODE(mode) if mode else 0o644)
        if os.geteuid() == 0:
            os.chown(temporary, uid, gid)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def make_backup(root: Path, plan: dict[Path, bytes]) -> tuple[Path, dict[Path, tuple[bytes | None, tuple[int, int, int]]]]:
    backup_root_raw = os.environ.get("BLACKLORD_THEME_BACKUP_ROOT", "/var/backups/blacklord-theme")
    backup_root = Path(backup_root_raw)
    if not backup_root.is_absolute():
        fail("backup location must be an absolute path")
    backup_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    backup_root = backup_root.resolve(strict=True)
    if backup_root == root or root in backup_root.parents:
        fail("backup location must be outside the web root")
    os.chmod(backup_root, 0o700)
    name = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
    backup_dir = backup_root / name
    backup_dir.mkdir(mode=0o700)
    originals: dict[Path, tuple[bytes | None, tuple[int, int, int]]] = {}
    manifest = []
    for target in plan:
        if target.is_symlink():
            fail("refusing to back up a symlinked target")
        if target.exists():
            data = target.read_bytes()
            metadata = copy_metadata(target)
            originals[target] = (data, metadata)
            relative = target.relative_to(root)
            stored = backup_dir / relative
            stored.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(stored, data, metadata)
            manifest.append({"path": str(relative), "state": "backed_up", "sha256": hashlib.sha256(data).hexdigest()})
        else:
            default_mode = 0o664 if target == root / CONFIG_REL else 0o644
            originals[target] = (None, copy_metadata(target, default_mode))
            manifest.append({"path": str(target.relative_to(root)), "state": "created_by_installer"})
    (backup_dir / "manifest.json").write_text(json.dumps({"version": 1, "files": manifest}, indent=2) + "\n", encoding="utf-8")
    os.chmod(backup_dir / "manifest.json", 0o600)
    return backup_dir, originals


def restore_originals(originals: dict[Path, tuple[bytes | None, tuple[int, int, int]]]) -> None:
    for path, (data, metadata) in reversed(list(originals.items())):
        try:
            if data is None:
                if path.exists() and not path.is_dir():
                    path.unlink()
            else:
                atomic_write(path, data, metadata)
        except Exception:
            pass


def clear_laravel_caches(root: Path) -> None:
    if os.environ.get("BLACKLORD_THEME_SKIP_ARTISAN") == "1":
        return
    php = shutil.which("php")
    if not php:
        fail("PHP CLI is required to clear the Panel route and view caches")
    for command in ("route:clear", "view:clear"):
        try:
            result = subprocess.run(
                [php, "artisan", command], cwd=root, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False, timeout=120,
            )
        except Exception:
            fail("could not clear a Laravel cache")
        if result.returncode != 0:
            fail("Laravel cache clear failed")


def install(panel_root: str, package_root: str, version: str) -> Path:
    package = Path(package_root).resolve(strict=True)
    manifest, files = load_and_verify_package(package, version)
    root = safe_panel_root(panel_root)
    for relative in ("public/assets", "app/Providers", "routes", "resources/views/layouts", "resources/views/templates", "resources/views/admin"):
        target = root / relative
        if not target.is_dir() or target.is_symlink():
            fail("Panel directory structure does not match the supported layout")
    for relative in ("artisan", PROVIDER_REL, ROUTES_REL, ADMIN_LAYOUT_REL, CLIENT_LAYOUT_REL):
        if not (root / relative).is_file() or (root / relative).is_symlink():
            fail("a required Pterodactyl source file is missing")

    plan = prepare_plan(root, package, version, files)
    backup_dir, originals = make_backup(root, plan)
    try:
        for path, data in plan.items():
            atomic_write(path, data, originals[path][1])
        clear_laravel_caches(root)
    except Exception:
        restore_originals(originals)
        try:
            clear_laravel_caches(root)
        except Exception:
            pass
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise
    return backup_dir


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: install-theme.py PANEL_ROOT PACKAGE_ROOT THEME_VERSION", file=sys.stderr)
        return 2
    try:
        backup = install(argv[1], argv[2], argv[3])
    except Exception as exc:
        print(f"Blacklord theme installation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Blacklord signed-in theme {argv[3]} installed. Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
