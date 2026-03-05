# Theme Architecture Analysis

**Date:** 2026-03-05
**Target Theme:** Twenty Twenty-Five (v1.4)
**Type:** Block Theme (Full Site Editing / FSE)

## 1. Structure Overview
Analysis of the runtime container confirmed the following structure:

- **`theme.json`**: Present. Acts as the central configuration engine (Global Styles, Settings).
- **Templates**: HTML-based files in `templates/` (e.g., `home.html`, `single.html`).
- **Parts**: HTML-based partials in `parts/` (e.g., `header.html`, `footer.html`).
- **Patterns**: PHP-based patterns in `patterns/`.

## 2. Inheritance Strategy
Since this is an FSE theme, the classic PHP template hierarchy is replaced by block templates. However, the **Child Theme** mechanism still applies for:
1.  `theme.json` merging (Child overrides Parent).
2.  `style.css` (CSS overrides).
3.  `functions.php` (Custom PHP logic).
4.  Custom Templates (Child `templates/home.html` overrides Parent).

## 3. Conclusion
We will provision `bloomscape-child` to encapsulate all Bloomscape-specific customizations, ensuring the parent theme can be updated securely.