# ADR-008: Theme Strategy - Child Theme Adoption

- **Status:** Accepted
- **Date:** 2026-03-05
- **Decision Owner:** Architect
- **Stage:** B (Baseline)

## 1. Context
Bloomscape requires a custom design system and layout structure. The base platform is WordPress 6.7+ with the default Twenty Twenty-Five theme (FSE). We need a strategy to apply customizations without losing the ability to update the core theme.

## 2. Decision
We will create and use a **Child Theme** (`bloomscape-child`) inherited from `twentytwentyfive`.

## 3. Detailed Design
- **Parent:** `twentytwentyfive`
- **Configuration:** `theme.json` in the child theme will inherit from the parent, overriding specific color palettes, typography, and layout settings.
- **Templates:** Custom templates will be placed in the child theme's `templates/` directory.
- **Logic:** Custom PHP logic will reside in `functions.php` or dedicated plugins, keeping the theme focused on presentation.

## 4. Consequences
- **Pros:** Safety of updates, clear separation of "Vendor" code vs "Custom" code.
- **Cons:** Slight complexity in managing `theme.json` inheritance (need to ensure keys are merged correctly by WP Core).