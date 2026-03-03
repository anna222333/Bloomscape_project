# 1. Context & Purpose
Mapping the Bloomscape reference site catalog structure to WooCommerce entities (Products, Categories, Attributes, Tags) to ensure an accurate structural baseline for Stage B.

## 2. Categories (`product_cat`)
Hierarchical structure for primary navigation:
*   **Plants** (slug: `plants`)
    *   Indoor Plants (`indoor-plants`)
    *   Pet Friendly (`pet-friendly`)
    *   New Arrivals (`new-arrivals`)
*   **Pots & Planters** (slug: `pots`)
*   **Care Tools** (slug: `care-tools`)

## 3. Global Attributes (`wc_product_attribute`)
Used for variable products and layered sidebar filtering (faceted search).
*   **Size** (`pa_size`) 
    *   Terms: Small (4-6 inch) `small`, Medium (8-10 inch) `medium`, Large (12+ inch) `large`, Extra Large `xl`
*   **Difficulty** (`pa_difficulty`) 
    *   Terms: Easy Care `easy`, Moderate `moderate`, Expert `expert`
*   **Light Level** (`pa_light`) 
    *   Terms: Low Light `low`, Indirect Bright `indirect`, Direct Sun `direct`

## 4. Tags (`product_tag`)
Non-hierarchical descriptors used for merchandising and specific behavioral traits:
*   `Air Purifying`
*   `Low Maintenance`
*   `Trailing`
*   `Upright`

## 5. Product Types
*   **Variable Products**: Core plants. Variations are built primarily on **Size** and/or **Pot Color**.
*   **Simple Products**: Accessories, individual care tools, soil.