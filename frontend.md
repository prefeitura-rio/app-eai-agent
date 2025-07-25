# Frontend Analysis and Refactoring Plan

This document provides an analysis of the current frontend structure and a plan to refactor the imports to match the new structure.

## 1. Current File Structure Analysis

Based on my analysis, the current file structure in `src/frontend/app` is as follows:

```
app/
├── components/
│   ├── header.tsx
│   ├── theme-provider.tsx
│   └── theme-toggle-button.tsx
├── experiments/
│   ├── [dataset_id]/
│   │   ├── [experiment_id]/
│   │   │   └── page.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── datasets-client.tsx
│   │   ├── dataset-experiments-client.tsx
│   │   └── experiment-details-client.tsx
│   ├── layout.tsx
│   └── page.tsx
├── favicon.ico
├── globals.css
├── layout.tsx
└── page.tsx
```

The key change is that the page-specific client components are now located in `app/experiments/components/`. The global components (`header`, `theme-provider`, `theme-toggle-button`) are in `app/components/`.

## 2. Refactoring Plan

To align the codebase with this new structure, the following import statements need to be updated:

1.  **`app/experiments/page.tsx`:**
    *   The import for `DatasetsClient` needs to be changed from `./components/datasets-client` to `./experiments/components/datasets-client`.

2.  **`app/experiments/[dataset_id]/page.tsx`:**
    *   The import for `DatasetExperimentsClient` needs to be changed from `../../components/dataset-experiments-client` to `./components/dataset-experiments-client`.

3.  **`app/experiments/[dataset_id]/[experiment_id]/page.tsx`:**
    *   The import for `ExperimentDetailsClient` needs to be changed from `../../../components/experiment-details-client` to `../../components/experiment-details-client`.

4.  **`app/experiments/layout.tsx`:**
    *   The import for `ExperimentsHeader` needs to be changed from `../components/header` to `../../components/header`.

I will now proceed with these changes.