# Theme Architecture Analysis: Twenty Twenty-Five

## 1. Executive Summary
- **Target Theme:** Twenty Twenty-Five (v1.4)
- **Architecture Type:** Block Theme (Full Site Editing / FSE)
- **Configuration Engine:** `theme.json` (Global Styles & Settings)
- **Template Engine:** HTML-based Block Templates

## 2. Structural Analysis
The theme adheres to the standard WordPress FSE structure found in `/var/www/html/wp-content/themes/twentytwentyfive`:

### 2.1 Core Configuration
- **`theme.json`**: The central source of truth for:
  - Color palettes (Bloomscape identity must be defined here).
  - Typography settings.
  - Layout constraints (content width, padding).
  - Block defaults (button styles, heading sizes).

### 2.2 Template Hierarchy (`/templates`)
HTML files defining the block structure for specific views:
- `home.html`: Homepage layout.
- `single.html`: Single post layout.
- `archive.html`: General archive layout.
- `404.html`: Error page.
- `search.html`: Search results.

### 2.3 Template Parts (`/parts`)
Reusable semantic sections:
- `header.html` / `header-large-title.html`
- `footer.html` / `footer-newsletter.html`
- `sidebar.html`

### 2.4 Patterns (`/patterns`)
PHP files containing block markup for complex UI compositions (e.g., banners, pricing tables).

## 3. WooCommerce Integration Strategy
As a Block Theme, Twenty Twenty-Five delegates WooCommerce rendering to Block templates.
- **Constraint:** Classic PHP hooks (`woocommerce_before_main_content`) behave differently or require specific block equivalents.
- **Requirement:** Bloomscape's specific product layouts (e.g., "Care Difficulty" badges) must be implemented as **Block Patterns** or **Custom Blocks**, not hardcoded PHP templates, to maintain FSE compatibility.

## 4. Customization Vector
To align with Bloomscape's design system without forking the core theme:
1.  **Child Theme:** Essential for `functions.php` (custom logic) and `style.css`.
2.  **`theme.json` Override:** The child theme's `theme.json` will merge with the parent's, overriding specific values (colors, fonts).