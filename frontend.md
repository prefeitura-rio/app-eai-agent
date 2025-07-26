# UI Refactoring Plan (Revised)

  Current State:

   * Project Setup: We have successfully removed all Tailwind CSS dependencies and established a new, modular styling
     architecture using CSS Modules and a global design system in globals.css.
   * Login Page: The login page (/login) has been completely redesigned with a modern, user-friendly interface that includes
     a theme toggle.
   * Home Page: The main dashboard (/) has been redesigned. It features a consistent, top-aligned header, a welcoming title,
     and a responsive two-column grid for navigation cards.
   * Experiments Page (`/experiments`):
       * The shared header is now fully responsive and displays context-aware titles and buttons.
       * The datasets table page is styled in a card, but we are still finalizing its responsiveness to ensure it looks
         perfect on all screen sizes.

  Next Steps:

   1. Finalize Datasets Table Responsiveness: Our immediate next step is to perfect the responsiveness of the datasets
      table on the /experiments page, ensuring it looks and functions correctly on all devices, especially on medium-sized
      screens.
   2. Refactor Dataset-Specific Page (`/experiments/[dataset_id]`): Once the main datasets page is complete, we will move
      on to the page for a specific dataset. This involves:
       * Implementing the tabbed interface to switch between "Experimentos" and "Exemplos".
       * Styling the "Experimentos" table, including the custom progress bars for metrics.
       * Styling the "Exemplos" table and implementing the "Load More" functionality.
   3. Refactor Experiment Details Page (`/experiments/[dataset_id]/[experiment_id]`): Finally, we will style the deepest
      level of the experiments section, focusing on a clear and organized presentation of the run details, comparisons, and
      evaluations.

  When you are ready to resume, we will pick up with perfecting the responsiveness of the datasets table.
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