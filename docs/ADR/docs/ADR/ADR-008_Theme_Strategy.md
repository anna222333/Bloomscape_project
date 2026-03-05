# ADR-008: Theme Customization Strategy (Child Theme vs. Fork)

- **Status:** Accepted
- **Date:** 2026-03-05
- **Decision Owner:** Architect
- **Stage:** B
- **Related:** `docs/DISCOVERY/THEME_ARCHITECTURE.md`

## 1. Context
Bloomscape requires a distinct visual identity and specialized WooCommerce functionality (e.g., specific product attributes display). The base theme, Twenty Twenty-Five, is a Full Site Editing (FSE) Block Theme. We must determine the optimal strategy for customization that balances maintainability with flexibility.

## 2. Options Considered

### Option A: Direct Modification
Modify the `twentytwentyfive` files directly.
- **Pros:** Immediate results.
- **Cons:** **Critical Risk.** All changes are lost upon theme update. Violates standard WordPress development practices.

### Option B: Theme Forking (Cloning)
Copy `twentytwentyfive` to a new `bloomscape-theme` and maintain it independently.
- **Pros:** Absolute control over all assets. No dependency on upstream changes.
- **Cons:** High maintenance burden. We become responsible for security patches and compatibility updates for the underlying FSE logic.

### Option C: Child Theme (Recommended)
Create `bloomscape-child` inheriting from `twentytwentyfive`.
- **Pros:**
  - Inherits upstream security/feature updates.
  - Isolates Bloomscape-specific logic (`functions.php`) and styles (`theme.json`).
  - Standard, recommended WordPress architectural pattern.
- **Cons:** Requires understanding of FSE inheritance (e.g., how `theme.json` merges).

## 3. Decision
We will implement **Option C: Child Theme**.

## 4. Implementation Strategy
The `bloomscape-child` theme will be provisioned in Stage B/C with the following structure:
1.  **`style.css`**: Defines the theme metadata and Template: twentytwentyfive.
2.  **`functions.php`**: Enqueues assets and registers custom block patterns/styles.
3.  **`theme.json`**: Overrides the parent configuration (Palette, Typography) to match Bloomscape Brand Guidelines.
4.  **`templates/`**: Custom HTML templates for WooCommerce views (e.g., `single-product.html`) if the parent defaults are insufficient.

## 5. Consequences
- **Positive:** Maintenance is decoupled from the base theme.
- **Negative:** We must monitor major Twenty Twenty-Five updates for breaking changes in the template structure.