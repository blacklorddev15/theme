# Blacklord signed-in Pterodactyl theme

This package is the current signed-in theme source used by the Telegram bot. The bot downloads the package files from this repository's `signed-in-dashboard-theme/` directory, verifies every file against `manifest.json`, and only then sends the installer and assets to the Panel VPS through SSH.

## What it installs

The package includes the illustrated background, dark glass cards, yellow-green accents, signed-in bottom navigation, and the Admin → Theme & Branding editor. Company Name stays editable; background image URL and both theme colors stay editable. An existing `public/panel-theme.json` is preserved, so a re-install does not overwrite the panel's current values.

It changes signed-in client/admin assets, the Admin theme route and sidebar link, the Theme & Branding controller/view, and the narrow SettingsServiceProvider behavior needed to keep Company Name editable in environment-only mode. It does not modify `resources/views/templates/auth/core.blade.php`, the login stylesheet, or the login page's assets.

## Safety and compatibility

Use the bot command `/installtema` from the configured owner's private Telegram chat. The bot provides a one-use HTTPS form for the target VPS SSH details and Panel directory; do not send those credentials in Telegram. The package is allowlisted and SHA-256 checked before SSH starts. It requires a compatible Pterodactyl Panel source layout and a PHP CLI. Unsupported source anchors fail closed.

Before changing files, the installer backs up only the affected theme files and Panel templates under `/var/backups/blacklord-theme/`, outside the Panel web root. It clears Laravel route/view caches after installation and attempts to roll back the affected files if installation or cache clearing fails. Existing Panel settings are not copied into this repository or the bot bundle.

## Package maintenance

When the theme changes, update the source files and `manifest.json` together. `manifest.json` records the exact byte size and SHA-256 digest for every runtime file; the bot rejects missing, extra, oversized, or mismatched files. Run `python3 -m unittest discover -s signed-in-dashboard-theme/tests` before publishing.
