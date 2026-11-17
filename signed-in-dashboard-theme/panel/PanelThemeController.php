<?php

namespace Pterodactyl\Http\Controllers\Admin;

use Illuminate\Contracts\Console\Kernel;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Prologue\Alerts\AlertsMessageBag;
use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;
use Pterodactyl\Http\Controllers\Controller;

class PanelThemeController extends Controller
{
    private const DEFAULTS = [
        'primaryColor' => '#ffff00',
        'secondaryColor' => '#00ff00',
        'backgroundUrl' => '',
    ];

    public function __construct(
        private AlertsMessageBag $alert,
        private SettingsRepositoryInterface $settings,
        private Kernel $kernel,
    ) {
    }

    public function index(): View
    {
        return view('admin.panel-theme', [
            'theme' => $this->readTheme(),
            'companyName' => config('app.name', 'Pterodactyl'),
        ]);
    }

    public function update(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'company_name' => ['required', 'string', 'max:191'],
            'primary_color' => ['required', 'regex:/^#[0-9a-fA-F]{6}$/'],
            'secondary_color' => ['required', 'regex:/^#[0-9a-fA-F]{6}$/'],
            'background_url' => ['nullable', 'string', 'max:2048', 'url', 'regex:/^https?:\\/\\//i'],
        ]);

        $data = [
            'primaryColor' => strtolower($validated['primary_color']),
            'secondaryColor' => strtolower($validated['secondary_color']),
            'backgroundUrl' => trim((string) ($validated['background_url'] ?? '')),
        ];
        $path = public_path('panel-theme.json');
        $temporaryPath = $path . '.tmp';
        $json = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);

        if ($json === false || file_put_contents($temporaryPath, $json, LOCK_EX) === false || ! @rename($temporaryPath, $path)) {
            @unlink($temporaryPath);
            $this->alert->danger('Could not save the theme configuration. Check the public folder permissions.')->flash();
            return redirect()->route('admin.theme');
        }

        @chmod($path, 0664);
        $this->settings->set('settings::app:name', trim($validated['company_name']));
        $this->kernel->call('queue:restart');
        $this->alert->success('Company name and theme settings saved. Refresh the panel to see the changes.')->flash();

        return redirect()->route('admin.theme');
    }

    private function readTheme(): array
    {
        $saved = [];
        $path = public_path('panel-theme.json');
        if (is_file($path)) {
            $decoded = json_decode((string) file_get_contents($path), true);
            if (is_array($decoded)) {
                $saved = $decoded;
            }
        }

        $theme = self::DEFAULTS;
        foreach (self::DEFAULTS as $key => $default) {
            if (isset($saved[$key]) && is_string($saved[$key])) {
                $theme[$key] = $saved[$key];
            }
        }

        if (! preg_match('/^#[0-9a-fA-F]{6}$/', $theme['primaryColor'])) {
            $theme['primaryColor'] = self::DEFAULTS['primaryColor'];
        }
        if (! preg_match('/^#[0-9a-fA-F]{6}$/', $theme['secondaryColor'])) {
            $theme['secondaryColor'] = self::DEFAULTS['secondaryColor'];
        }
        if ($theme['backgroundUrl'] !== '' && (! filter_var($theme['backgroundUrl'], FILTER_VALIDATE_URL) || ! preg_match('/^https?:\\/\\//i', $theme['backgroundUrl']))) {
            $theme['backgroundUrl'] = '';
        }

        return $theme;
    }
}
