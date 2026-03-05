# STAGE C: HOMEPAGE & GLOBAL STYLES (Active)

## 1. Stage Purpose
Transform the blank `bloomscape-child` theme into a visual replica of Bloomscape using Full Site Editing (FSE) standards.

## 2. Technical Strategy (Per ADR-008)
- **Configuration:** All global styles (colors, fonts, spacing) MUST be defined in `theme.json`. Do not use hardcoded CSS for global values.
- **Templates:** Use HTML block templates (`templates/front-page.html`) instead of PHP.
- **Components:** Use Template Parts for Header/Footer.

## 3. Work Breakdown

### Step C1: Global Styles (`theme.json`)
- **Action:** Extract colors and typography from reference.
- **Deliverable:** Updated `theme.json` in child theme.
- **Validation:** Site verifies correct palette in Site Editor.

### Step C2: Header & Navigation
- **Action:** Create `parts/header.html`.
- **Content:** Logo (Text/Image), Navigation Menu (Plants, Care, etc.), Cart Icon.
- **Validation:** Header appears on all pages.

### Step C3: Homepage Hero Section
- **Action:** Create `templates/front-page.html`.
- **Block Structure:** Cover Block (Full width image) + Heading + CTA Button.
- **Assets:** Use existing assets in `docs/assets/` or placeholders.

### Step C4: Product Categories Grid
- **Action:** Add to Homepage.
- **Block:** Columns Block or Query Loop.
- **Data:** Display seeded categories (Plants, Care Tools).

## 4. Acceptance Criteria (QG-C)
- [