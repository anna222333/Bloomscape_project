# Theme Architecture Analysis: Twenty Twenty-Five

## 1. Overview
- **Base Theme:** Twenty Twenty-Five
- **Version:** 1.4
- **Type:** Full Site Editing (FSE) / Block Theme
- **Core Config:** `theme.json`

## 2. File Structure Analysis
Based on inspection of `/var/www/html/wp-content/themes/twentytwentyfive`:

### Templates (`/templates`)
Standard HTML block templates detected:
- `home.html` (Homepage)
- `single.html` (Single Post)
- `archive.html` (Generic Archive)
- `404.html` (Not Found)
- `search.html` (Search Results)

### Template Parts (`/parts`)
Modular components:
- `header.html`, `header-large-title.html`
- `footer.html`, `footer-newsletter.html`
- `sidebar.html`

### Patterns (`/patterns`)
PHP-based block patterns utilized for complex layouts:
- `banner-intro.php`
- `banner-poster.php`

## 3. WooCommerce Compatibility
- Native block theme support expected.
- Customization requires:
    1. Overriding `theme.json` for Bloomscape palette/typography.
    2. Creating specific `woocommerce` block templates (e.g., `single-product.html`, `archive-product.html`) in the child theme if the base theme defaults are insufficient.

## 4. Risks & Constraints
- **FSE Learning Curve:** Layouts are defined in HTML with block markup, not PHP. Logic must reside in blocks or `functions.php`.
- **Plugin Conflicts:** Some classic WooCommerce plugins may not render correctly inside Block templates without legacy hooks.