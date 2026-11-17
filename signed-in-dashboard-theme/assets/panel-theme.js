(function () {
    'use strict';

    var defaults = {
        primaryColor: '#ffff00',
        secondaryColor: '#00ff00',
        backgroundUrl: ''
    };

    function hexToRgb(hex) {
        if (typeof hex !== 'string' || !/^#[0-9a-f]{6}$/i.test(hex)) return null;
        return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
    }

    function safeBackground(value) {
        if (typeof value !== 'string' || !value.trim()) return '';
        try {
            var parsed = new URL(value.trim(), window.location.origin);
            return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '';
        } catch (_) {
            return '';
        }
    }

    function setBackground(url) {
        var body = document.body;
        if (!body) return;
        var client = body.classList.contains('bg-neutral-800');
        var adminSurfaces = document.querySelectorAll('body.skin-blue .wrapper, body.skin-blue .content-wrapper, body.skin-blue .right-side');

        if (!url) {
            body.style.removeProperty('background-image');
            body.style.removeProperty('background-size');
            body.style.removeProperty('background-position');
            body.style.removeProperty('background-repeat');
            body.style.removeProperty('background-attachment');
            adminSurfaces.forEach(function (node) {
                node.style.removeProperty('background-image');
                node.style.removeProperty('background-size');
                node.style.removeProperty('background-position');
                node.style.removeProperty('background-repeat');
                node.style.removeProperty('background-attachment');
            });
            return;
        }

        var image = 'url(' + JSON.stringify(url) + ')';
        if (client) {
            body.style.setProperty('background-image', 'linear-gradient(180deg, rgba(5, 3, 15, .5), rgba(5, 3, 15, .85)), ' + image + ', radial-gradient(circle at 50% 0%, #2a1065 0%, #0a0620 55%, #03020a 100%)', 'important');
            body.style.setProperty('background-size', 'cover', 'important');
            body.style.setProperty('background-position', 'center', 'important');
            body.style.setProperty('background-repeat', 'no-repeat', 'important');
            body.style.setProperty('background-attachment', 'fixed', 'important');
        }
        adminSurfaces.forEach(function (node) {
            node.style.setProperty('background-image', 'linear-gradient(rgba(5, 3, 15, .78), rgba(5, 3, 15, .9)), ' + image, 'important');
            node.style.setProperty('background-size', 'cover', 'important');
            node.style.setProperty('background-position', 'center', 'important');
            node.style.setProperty('background-repeat', 'no-repeat', 'important');
            node.style.setProperty('background-attachment', 'fixed', 'important');
        });
    }

    function apply(settings) {
        var primary = hexToRgb(settings.primaryColor) ? settings.primaryColor.toLowerCase() : defaults.primaryColor;
        var secondary = hexToRgb(settings.secondaryColor) ? settings.secondaryColor.toLowerCase() : defaults.secondaryColor;
        var p = hexToRgb(primary);
        var s = hexToRgb(secondary);
        var root = document.documentElement;
        root.style.setProperty('--panel-theme-primary', primary);
        root.style.setProperty('--panel-theme-secondary', secondary);
        root.style.setProperty('--accent-rgb', p.join(', '));
        root.style.setProperty('--accent2-rgb', s.join(', '));
        root.style.setProperty('--accent', 'rgb(' + p.join(', ') + ')');
        root.style.setProperty('--accent2', 'rgb(' + s.join(', ') + ')');
        root.style.setProperty('--glow', 'rgba(' + p.join(', ') + ', .35)');
        root.style.setProperty('--line', 'rgba(' + p.join(', ') + ', .38)');
        setBackground(safeBackground(settings.backgroundUrl));
    }

    function init() {
        apply(defaults);
        fetch('/panel-theme.json?v=' + Date.now(), { cache: 'no-store', credentials: 'same-origin' })
            .then(function (response) { return response.ok ? response.json() : null; })
            .then(function (settings) {
                if (settings && typeof settings === 'object') apply(settings);
            })
            .catch(function () {});
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
