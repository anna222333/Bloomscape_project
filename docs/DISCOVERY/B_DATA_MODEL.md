# Bloomscape Data Model (Baseline v1.0)

**Status:** APPROVED
**Date:** 2026-02-16
**Context:** Defines the taxonomy and structure for the initial WooCommerce setup.

## 1. Product Categories (Hierarchical Taxonomy)
*Target Taxonomy: `product_cat`*

- **Plants** (Parent) - `plants`
    - **Indoor Plants** - `indoor-plants`
    - **Outdoor Plants** - `outdoor-plants`
    - **Pet Friendly** - `pet-friendly`
    - **Easy Care** - `easy-care`
- **Care & Tools** (Parent) - `care-tools`
    - **Potting Mixes** - `potting-mixes`
    - **Tools** - `tools`
    - **Watering** - `watering`
- **Pots & Planters** - `pots`

## 2. Product Attributes (Global Attributes)
*Target Taxonomy: `pa_<slug>`*
*Used for: Filtering, Variations*

### A. Size (`pa_size`)
- X-Small
- Small
- Medium
- Large
- X-Large

### B. Light Requirement (`pa_light`)
- Low Light
- Partial Sunlight
- Bright Direct Light

### C. Difficulty (`pa_difficulty`)
- No-Fuss (Beginner)
- Easy
- Moderate

### D. Pet Toxicity (`pa_pet_friendly`)
- Pet Friendly
- Toxic to Pets

## 3. Product Types Mapping
- **Variable Product:** Live Plants (Variations: Pot Color, Size).
- **Simple Product:** Tools, Soil bags.
- **Grouped Product:** Plant Sets (Trios).

## 4. Custom Fields (Meta Data)
*Target: `wp_postmeta`*
- `_botanical_name`: Scientific name (e.g., *Sansevieria*).
- `_care_guide_url`: Link to specific care page.