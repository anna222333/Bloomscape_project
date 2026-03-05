# ADR-008: Theme Customization Strategy (Child Theme)

- **Status:** Accepted
- **Date:** 2026-03-05
- **Decision Owner:** Architect
- **Stage:** B
- **Related:** `docs/DISCOVERY/THEME_ARCHITECTURE.md`

## 1. Context
We need to implement the Bloomscape visual identity and WooCommerce functionality on top of the `twentytwentyfive` (FSE) theme. We must decide how to manage these customizations.

## 2. Options Considered
1.  **Direct Modification:** Edit `twentytwentyfive` files directly.
    - *Pros:* Fastest initially.
    - *Cons:* Changes lost on theme update. Security risk.
2.  **Cloning:** Copy `twentytwentyfive` to `bloomscape-theme` and treat as a new root theme.
    - *Pros:* Full control.
    - *Cons:* We become responsible for all maintenance and security backports.
3.  **Child Theme:** Create `bloomscape-child` that inherits from `twentytwentyfive`.
    - *Pros:* Inherits updates, isolates custom code, standard WP practice.
    - *Cons:* Slightly complex with FSE (merging `theme.json`), but supported by WordPress 6.x.

## 3. Decision
We will use **Option 3: Child Theme**.

## 4. Implementation Details
- **Name:** `bloomscape-child`
- **Structure:**
    - `style.css` (Meta + CSS overrides)
    - `functions.php` (Enqueues, custom hooks)
    - `theme.json` (Overrides for colors, fonts, layout)
    - `templates/` (Custom FSE templates for WooCommerce)