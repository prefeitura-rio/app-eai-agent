# Frontend Refactoring Plan: Replicating the Original Design & Adding Authentication

This document outlines the step-by-step plan to refactor the new Next.js frontend to perfectly match the design and functionality of the original application, and to add a robust authentication system.

---

## Part 1: Authentication Flow Implementation

Before styling, we will implement a complete authentication system.

### 1. Install Dependencies
We'll need a library to manage cookies on the client-side. `js-cookie` is a popular and lightweight choice.

### 2. Create an Authentication Context
A React Context will provide a global state for authentication, making it easy to access the user's token and login/logout functions from any component.

**File to Create:** `app/contexts/AuthContext.tsx`

**Plan:**
1.  Create an `AuthContext` that stores the auth token and user state.
2.  Create an `AuthProvider` component that will wrap the entire application.
3.  The `AuthProvider` will:
    *   Use `useState` to hold the token.
    *   Use `useEffect` to initialize the token from the browser's cookies on initial load.
    *   Provide `login` and `logout` functions.
        *   `login(token)`: Will save the token to a cookie and update the state.
        *   `logout()`: Will remove the token from the cookie and clear the state.
4.  Create a custom hook `useAuth()` for easy access to the context.

### 3. Create the Login Page
This will be the public-facing page where users enter their credentials.

**File to Create:** `app/login/page.tsx`

**Plan:**
1.  Create a simple, centered form with fields for credentials (e.g., username/password or a single token field).
2.  The component will be a Client Component (`'use client'`).
3.  On form submission, it will:
    *   Make a `POST` request to the FastAPI backend's token endpoint (e.g., `/api/v1/token`).
    *   If the request is successful, it will receive the Bearer Token.
    *   It will call the `login()` function from the `AuthContext` to store the token.
    *   It will then redirect the user to the main `/experiments` page.
    *   It will display loading and error states to the user.

### 4. Implement Middleware for Route Protection
Middleware is the core of Next.js route protection. It will run on the server before any page is rendered, checking if the user is authenticated.

**File to Create:** `middleware.ts` (at the root of the `src/frontend` directory)

**Plan:**
1.  The middleware will check for the presence of the auth token in the request's cookies.
2.  It will define which routes are protected (e.g., `/experiments` and all its sub-routes).
3.  **Logic:**
    *   If a user tries to access a protected route **without** a token, they will be redirected to `/login`.
    *   If a user is already logged in (has a token) and tries to access `/login`, they will be redirected to `/experiments`.
    *   All other requests will be allowed to proceed.

### 5. Integrate Authentication into API Calls
All existing `fetch` requests to the backend need to be updated to include the authentication token.

**Files to Modify:** All page components that fetch data (`/experiments/...`).

**Plan:**
1.  In each component that makes an API call, use the `useAuth()` hook to get the token.
2.  Add the `Authorization: Bearer <token>` header to every `fetch` request.

---

## Part 2: UI/Style Refactoring (To be executed after authentication is complete)

This section details the plan to replicate the original application's design and feel.

### 1. Tailwind CSS Theme Configuration
Translate the CSS variables from `experiment.css` into Tailwind's theme configuration in `tailwind.config.js`. This includes colors, fonts, border-radius, and box-shadows.

### 2. Global Layout and Header
Update `app/experiments/layout.tsx` and `app/components/header.tsx` to match the original's padding, font sizes, and button styles, using the new Tailwind theme.

### 3. Datasets Page (`/experiments`)
In `app/experiments/components/datasets-client.tsx`, replicate the card-based layout, table styles (header, rows, hover effects, badges), and search bar design.

### 4. Dataset Experiments Page (`/experiments/[dataset_id]`)
In `app/experiments/components/dataset-experiments-client.tsx`, implement the tabbed interface and style the experiments table, including dynamic metric columns with progress bars and the examples table with markdown rendering.

### 5. Experiment Details Page (`/experiments/[dataset_id]/[experiment_id]`)
This is the most complex part. In `app/experiments/components/experiment-details-client.tsx`:
1.  **Layout:** Replicate the two-column layout (fixed run list, scrollable content).
2.  **Run List:** Style the list items with hover/active states and add the filter section.
3.  **Main Content:**
    *   Re-create the card-based layout for metadata and summary metrics.
    *   Replicate the two-column comparison view.
    *   Re-create the evaluation cards with score badges and expandable sections.
    *   Build the reasoning timeline component from scratch, styling each event type (reasoning, tool call, etc.) with its unique icon and color.