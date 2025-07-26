# Frontend Refactoring Plan: Vanilla to Next.js

This document outlines the detailed plan for migrating the legacy vanilla HTML, CSS, and JavaScript frontend to a modern Next.js application. The primary goal is to replicate the existing user interface and functionality while adhering to the new architecture.

**Core Technologies:**
- **Framework:** Next.js (with React Server and Client Components)
- **Styling:** Vanilla CSS with CSS Modules and Bootstrap 5 (already installed).
- **Language:** TypeScript

**Guiding Principles:**
- **Component-Based Architecture:** Break down pages into reusable React components.
- **Scoped Styles:** Use CSS Modules (`.module.css`) for component-specific styles to avoid global namespace conflicts.
- **Global Styles:** Use `src/frontend/app/globals.css` for base styles, design tokens (CSS variables), and Bootstrap overrides.
- **Data Fetching:** Utilize React Server Components for initial data fetching where possible, passing data to Client Components for interactive elements.
- **Source of Truth:** The original `static/` files will serve as the blueprint for the UI and functionality of each new page.

---

## Phase 1: Refactor Datasets Page (`/experiments`)

**Goal:** Recreate the main datasets dashboard, which lists all available datasets.

- **Original Source Files:**
    - `static/datasets.html`: Provides the HTML structure for the table and layout.
    - `static/datasets.js`: Contains the logic for fetching, displaying, filtering, and sorting datasets.
    - `static/experiment.css`: Contains the styling for the table, cards, and overall page appearance.

- **New Target Files:**
    - `src/frontend/app/experiments/page.tsx`: The main entry point for the route. This will be a Server Component responsible for fetching the initial list of datasets.
    - `src/frontend/app/experiments/components/DatasetsClient.tsx`: A Client Component that will receive the initial datasets and manage all interactive logic (search, sorting).
    - `src/frontend/app/experiments/page.module.css`: A CSS Module for styles specific to the datasets page.

### Detailed Implementation Steps:

1.  **`page.tsx` (Server Component):**
    -   Fetch the list of all datasets from the backend API.
    -   Render the main page layout, including the header.
    -   Pass the fetched dataset list as a prop to the `<DatasetsClient />` component.

2.  **`page.module.css` (CSS Module):**
    -   Extract relevant styles from `experiment.css` that apply to the datasets table, card, and search bar.
    -   Create classes for the main container, the card wrapper, and the table, adapting the styles to the CSS module format (e.g., `.table` becomes `.datasetsTable`).

3.  **`DatasetsClient.tsx` (Client Component):**
    -   **State Management:** Use `useState` to manage the list of datasets, the current search term, and the sorting state (column and direction).
    -   **HTML to JSX:** Convert the `<table>` structure from `datasets.html` into JSX. The table body will be rendered by mapping over the state-managed dataset list.
    -   **Interactivity:**
        -   **Search:** Implement the search functionality from `datasets.js`. An `onChange` handler on the search input will update the search term state and filter the displayed datasets.
        -   **Sorting:** Implement the sorting logic from `datasets.js`. `onClick` handlers on the table headers (`<th>`) will update the sorting state and re-sort the dataset list.
    -   **Styling:** Import `page.module.css` and apply the classes to the corresponding JSX elements.

---

## Phase 2: Refactor Dataset-Specific Page (`/experiments/[dataset_id]`)

**Goal:** Recreate the page that displays details for a single dataset, featuring a tabbed interface for "Experimentos" and "Exemplos".

- **Original Source Files:**
    - `static/dataset-experiments.html`: Provides the HTML for the tabs, tables, and modal.
    - `static/dataset-experiments.js`: Contains the logic for fetching data, handling tab switching, managing tables (sorting, filtering), and the "load more" functionality for examples.
    - `static/experiment.css`: Contains styles for the tabs, tables, and custom progress bars.

- **New Target Files:**
    - `src/frontend/app/experiments/[dataset_id]/page.tsx`: Server Component to fetch initial data for the specific dataset.
    - `src/frontend/app/experiments/components/DatasetExperimentsClient.tsx`: The main Client Component to manage the tabbed interface and its state.
    - `src/frontend/app/experiments/[dataset_id]/page.module.css`: Scoped styles for this page.
    - `src/frontend/app/experiments/components/ProgressBar.tsx`: A new, reusable component for displaying metric scores.
    - `src/frontend/app/experiments/components/ProgressBar.module.css`: Scoped styles for the `ProgressBar` component.

### Detailed Implementation Steps:

1.  **`page.tsx` (Server Component):**
    -   Fetch the initial dataset details, including the first page of experiments and examples.
    -   Render the page layout and pass the initial data to `<DatasetExperimentsClient />`.

2.  **`page.module.css` (CSS Module):**
    -   Create styles for the tab container (`.nav-tabs`), the active/inactive tab states, and the card that wraps the tab content.
    -   Extract table styles from `experiment.css` and adapt them for the "Experimentos" and "Exemplos" tables.

3.  **`ProgressBar.tsx` & `ProgressBar.module.css`:**
    -   Create a new component that accepts a `score` prop (a number between 0 and 1).
    -   The component will render the progress bar UI seen in `dataset-experiments.html`.
    -   The `ProgressBar.module.css` will contain the styles for the bar's container and the dynamic width/color based on the score, replicating the logic from `createMetricCell` in `dataset-experiments.js`.

4.  **`DatasetExperimentsClient.tsx` (Client Component):**
    -   **Tab Management:** Use `useState` to manage the active tab. Render Bootstrap's `Nav` and `Tab` components to create the tabbed interface.
    -   **"Experimentos" Tab:**
        -   Convert the experiments table from `dataset-experiments.html` to JSX.
        -   Use the new `<ProgressBar />` component to render the metric cells.
        -   Implement the search and sort functionality from `dataset-experiments.js`.
    -   **"Exemplos" Tab:**
        -   Convert the examples table to JSX.
        -   Implement the search filter.
        -   Implement the "Load More" functionality. A button click will trigger an API call to fetch the next page of examples and append them to the state.
        -   Recreate the "Example Details" modal using a React-based modal library or a custom component, populating it with data from the selected example row.

---

## Phase 3: Refactor Experiment Details Page (`/experiments/[dataset_id]/[experiment_id]`)

**Goal:** Recreate the detailed view for a single experiment run, including its parameters, metrics, comparisons, and reasoning timeline.

- **Original Source Files:**
    - `static/experiment.html`: Provides the two-column layout, metadata display, comparison view, and timeline structure.
    - `static/experiment.js`: Contains the logic for fetching run data, filtering runs, and rendering all the detailed views.
    - `static/experiment.css`: Contains specific styles for the two-column layout, timeline, evaluation cards, and summary metrics.

- **New Target Files:**
    - `src/frontend/app/experiments/[dataset_id]/[experiment_id]/page.tsx`: Server Component to fetch all data related to the specific experiment.
    - `src/frontend/app/experiments/components/ExperimentDetailsClient.tsx`: A Client Component to manage the state of the selected run and render all its details.
    - `src/frontend/app/experiments/[dataset_id]/[experiment_id]/page.module.css`: Scoped styles for the details page.

### Detailed Implementation Steps:

1.  **`page.tsx` (Server Component):**
    -   Fetch all necessary data for the experiment, including all its runs, metadata, and summary metrics.
    -   Render the main layout and pass all fetched data as props to `<ExperimentDetailsClient />`.

2.  **`page.module.css` (CSS Module):**
    -   Define the two-column layout using CSS (e.g., Flexbox or Grid), replicating the structure from `experiment.html` (`run-list-panel` and `main-content-wrapper`).
    -   Extract and adapt styles for the timeline, evaluation cards, comparison boxes, and metadata grid from `experiment.css`.

3.  **`ExperimentDetailsClient.tsx` (Client Component):**
    -   **State Management:** Use `useState` to manage the list of all runs, the currently selected `runId`, and any active filters.
    -   **Run List (Left Column):**
        -   Render the list of runs from the props.
        -   Implement `onClick` handlers to update the `selectedRunId` state.
        -   Implement the filtering logic from `experiment.js` to filter the displayed runs.
    -   **Details View (Right Column):**
        -   Conditionally render the details of the selected run based on `selectedRunId`.
        -   **Metadata:** Convert the metadata section from `experiment.html` to JSX.
        -   **Summary Metrics:** Replicate the summary metrics grid.
        -   **Comparison:** Recreate the "Resposta do Agente" vs. "Resposta de Referência" view.
        -   **Evaluations:** Map over the `annotations` of the selected run and render the evaluation cards, including the score and expandable explanation.
        -   **Reasoning Timeline:** Convert the timeline structure from `experiment.html` to JSX. Dynamically generate timeline items by mapping over the `ordered_steps` of the selected run, creating different content based on the step `type` (e.g., `reasoning_message`, `tool_call_message`).
