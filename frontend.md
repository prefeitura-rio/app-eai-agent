# UI Refactoring Plan (Revised)

This document outlines the step-by-step plan to refactor the UI of the `experiments` pages using a modular CSS architecture with CSS Modules and a centralized design system, based on the original HTML/CSS files provided in `GEMINI.md`.

### **Phase 1: Establish a Design System in `globals.css`**

1.  **Goal:** Create a consistent look and feel by defining a design system based on the original `experiment.css`. This will centralize design tokens.
2.  **Source File:** `static/experiment.css` (from `GEMINI.md`).
3.  **Target File:** `src/frontend/app/globals.css`.
4.  **Action:**
    *   Analyze `experiment.css` to identify foundational design tokens (colors, fonts, spacing, border-radius).
    *   Define these as CSS custom properties (variables) under the `:root` selector in `globals.css`. This will serve as the project's design system.
    *   Add any truly global styles (e.g., body background, link styles) that should apply everywhere.

### **Phase 2: Create Modular & Page-Specific Stylesheets**

1.  **Goal:** Create a structured and scoped styling system using CSS Modules.
2.  **Source File:** `static/experiment.css`.
3.  **Action:**
    *   **General Styles (`page.module.css`):** Create `src/frontend/app/experiments/page.module.css`. This file will contain styles that are shared across the different pages within the `/experiments` route, such as the main layout containers or common card styles.
    *   **Page-Specific Styles:** For styles that are unique to a single page, create dedicated CSS modules within that page's directory. For example:
        *   `src/frontend/app/experiments/[dataset_id]/page.module.css`
        *   `src/frontend/app/experiments/[dataset_id]/[experiment_id]/page.module.css`
    *   Strategically move relevant styles from the original `experiment.css` into these new, scoped module files.

### **Phase 3: Refactor Datasets Page (`/experiments`)**

1.  **Goal:** Replicate the UI of `datasets.html` using the new modular CSS architecture.
2.  **Source Files:** `datasets.html`, `datasets.js`.
3.  **Target Files:**
    *   `src/frontend/app/experiments/components/datasets-client.tsx`
    *   `src/frontend/app/experiments/page.module.css`
4.  **Detailed Plan:**
    *   Use the layout and structure from `datasets.html` as a blueprint.
    *   The styles for the main card and table structure will be defined in `page.module.css` and imported into `datasets-client.tsx`.
    *   Apply the modular classes (e.g., `styles.card`, `styles.table`) to the Bootstrap components, ensuring the styling is scoped.

### **Phase 4: Refactor Dataset-Specific Page (`/experiments/[dataset_id]`)**

1.  **Goal:** Replicate the tabbed UI from `dataset-experiments.html`.
2.  **Source Files:** `dataset-experiments.html`, `dataset-experiments.js`.
3.  **Target Files:**
    *   `src/frontend/app/experiments/components/dataset-experiments-client.tsx`
    *   `src/frontend/app/experiments/[dataset_id]/page.module.css`
4.  **Detailed Plan:**
    *   Create specific styles for the tabbed interface in `page.module.css`.
    *   The component will import these styles and apply them to the Bootstrap `nav-tabs`.
    *   The custom progress bars for metrics will be a reusable React component with its own CSS module (`ProgressBar.module.css`) to keep its logic and styling encapsulated.

### **Phase 5: Refactor Experiment Details Page (`/experiments/[dataset_id]/[experiment_id]`)**

1.  **Goal:** Style the experiment run details page consistently with the new design system.
2.  **Source Files:** `dataset-experiments.html` (for style inference).
3.  **Target Files:**
    *   `src/frontend/app/experiments/components/experiment-details-client.tsx`
    *   `src/frontend/app/experiments/[dataset_id]/[experiment_id]/page.module.css`
4.  **Detailed Plan:**
    *   The unique two-column layout for this page will be defined in its own `page.module.css`.
    *   The component will import these styles to structure the run list and the details view.
    *   The styling for cards and badges within this page will leverage the design tokens from `globals.css` and common component styles from the more general `experiments/page.module.css`.