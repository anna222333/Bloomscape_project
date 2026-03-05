# STAGE C: HOMEPAGE & GLOBAL STYLES

## 1. Stage Purpose
Transform the functional baseline into a visual replica of the Bloomscape homepage using WordPress FSE (Full Site Editing).

## 2. Goals
1.  **Design System:** Implement Bloomscape's color palette and typography in `theme.json`.
2.  **Structural Parts:** Build the Header (Logo + Nav) and Footer.
3.  **Homepage Content:** Implement the key sections:
    - Hero Section (Image + CTA).
    - "Shop by Category" Grid.
    - "New Arrivals" Product Query.

## 3. Technical Strategy
- **File-Based Architecture:** All templates (`front-page.html`) and parts (`header.html`) will be created as files in the Docker container, NOT in the DB editor.
- **Native Blocks:** Use Core Blocks (Group, Cover, Columns, Query Loop) wherever possible to avoid external dependencies.
- **CSS Variables:** Drive all styling through `theme.json` presets.

## 4. Task List
- [