# Loading the theme stylesheets

Copy every file in `assets/` to the panel's `public/assets/` directory. Keep the image filenames unchanged: the login CSS uses `luxury-reference-chair.jpg`, and the signed-in/admin background CSS uses `dashboard-background-2600169.png`.

Add the following links inside the `@section('assets')` section of `resources/views/templates/base/core.blade.php`:

```blade
<link rel="stylesheet" href="/assets/luxury-reference-login.css?v=theme-1">
<link rel="stylesheet" href="/assets/dashboard-background-2600169.css?v=theme-1">
<link rel="stylesheet" href="/assets/server-card-green-glow.css?v=theme-1">
<link rel="stylesheet" href="/assets/server-console-power-green.css?v=theme-1">
```

Add the login stylesheet inside `@section('assets')` in `resources/views/templates/auth/core.blade.php`:

```blade
<link rel="stylesheet" href="/assets/luxury-reference-login.css?v=theme-1">
```

Add the dashboard background stylesheet before `</head>` in `resources/views/layouts/admin.blade.php`:

```blade
<link rel="stylesheet" href="/assets/dashboard-background-2600169.css?v=theme-1">
```

Use a new query-string version after changing a CSS file so browsers do not keep an older cached copy. Check for existing links before inserting these to avoid duplicate loading. These are manual integration notes only; this repository does not contain a script that edits a live panel.
