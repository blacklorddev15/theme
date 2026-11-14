# Blacklord Green-Chair Theme

A source-level visual theme package for **Pterodactyl Panel 1.15.2**, collected from the current UI customizations. It is a set of assets and component overrides, not a Pterodactyl plugin or an automatic installer.

## What it includes

- A dark-green login design with no registration, Google, or Apple sign-in links in the login UI. The existing username/email and password login, CAPTCHA handling, password visibility control, and password-reset link remain in the supplied component source.
- The standard dashboard layout with the supplied green chair background, glowing-green server cards, and green Start, Restart, and Stop controls.
- A Company Name-only environment-mode override. It reads only the `settings::app:name` value from the database when environment-only mode is enabled; other settings continue to come from environment configuration.

The theme does not change the Company Name. The current value can remain **Pterodactyl**.

## Repository layout

- `assets/` contains the CSS overrides and the two background assets. Copy these files into the panel's `public/assets/` directory.
- `panel-source/` contains the four React/TypeScript component overrides under their Pterodactyl source paths. Use them with the matching 1.15.2 source tree and rebuild the frontend.
- `patches/company-name-only-settings-provider.patch` adds the narrowly scoped Company Name behavior to `SettingsServiceProvider`.
- `patches/stylesheet-installation.md` lists the Blade template stylesheet links needed to load the CSS.

## Applying it

Back up the panel files first and test against a matching Pterodactyl 1.15.2 source tree. Follow `patches/stylesheet-installation.md`, copy the component overrides to their matching source paths, then rebuild the frontend using the build procedure for that panel release. Apply the Company Name patch only if that behavior is wanted; it assumes `SettingsServiceProvider` is registered.

Keep `APP_ENVIRONMENT_ONLY=true`. Do not disable environment-only mode to apply this theme. The Company Name patch leaves the current value alone and does not modify authentication, server settings, or server data.

This repository contains no credentials, tokens, host addresses, live server allocations, or personal account data. It does not make changes to any running panel by itself.
