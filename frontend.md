## Part 2: Next.js, TypeScript, and CSS Best Practices

This section provides a comprehensive guide to best practices for building modern frontend applications using Next.js, TypeScript, and CSS.

### 1. Project Setup and Configuration

*   **Start with `create-next-app`**: Always use the official `create-next-app` CLI to bootstrap your project. It provides a robust, pre-configured TypeScript environment out of the box.
*   **Strict `tsconfig.json`**: Enable `strict: true` in your `tsconfig.json`. This activates all strict type-checking options and helps catch a wide range of potential errors during development.
*   **Organized Folder Structure**: A well-organized folder structure is key for maintainability. Group components by feature or by type (e.g., `ui`, `layout`, `shared`). Consider a structure like this:
    ```
    src/
    ├── app/
    ├── components/
    │   ├── ui/         # Reusable UI elements (Button, Input, etc.)
    │   ├── layout/     # Page layout components (Header, Footer, Sidebar)
    │   └── features/   # Components related to specific features
    ├── lib/            # Utility functions, helpers
    ├── styles/         # Global styles
    └── types/          # Shared TypeScript types
    ```

### 2. Component Development (React & TypeScript)

*   **Functional Components and Hooks**: Exclusively use functional components with React Hooks (`useState`, `useEffect`, `useContext`, etc.). Avoid class-based components.
*   **Strongly-Typed Props and State**: Always define explicit types for your component's props and state. This is the core benefit of TypeScript in a React context.
    ```tsx
    type UserProfileProps = {
      userId: string;
      name: string;
    };

    const UserProfile = ({ userId, name }: UserProfileProps) => {
      const [user, setUser] = useState<User | null>(null);
      // ...
    };
    ```
*   **Avoid `any`**: The `any` type is an escape hatch that disables type checking. Avoid it whenever possible. Use `unknown` for values where the type is truly unknown and perform type-checking before use.
*   **Custom Hooks for Reusable Logic**: Encapsulate reusable logic (like data fetching, event listeners, etc.) into custom hooks. This keeps your components clean and focused on rendering UI.
*   **Use Utility Types**: Leverage TypeScript's built-in utility types like `Partial`, `Pick`, `Omit`, and `Record` to manipulate and create new types without redundant definitions.

### 3. Styling (CSS)

*   **CSS Modules**: For component-level styles, use CSS Modules (`.module.css`). This automatically scopes class names, preventing global style conflicts. This is the recommended approach for most components in Next.js.
*   **Global Styles**: Use a global stylesheet (`globals.css`) for base styles, CSS variables (design tokens), and resets. Import it only in your root `layout.tsx`.
*   **Tailwind CSS (or other utility-first frameworks)**: Consider using a utility-first CSS framework like Tailwind CSS for rapid development. It pairs well with Next.js and component-based architecture.
*   **PostCSS**: Use PostCSS with plugins like `autoprefixer` to ensure cross-browser compatibility. `create-next-app` configures this for you.

### 4. Data Fetching

*   **Server Components for Data Fetching**: Whenever possible, fetch data in Server Components. This reduces client-side bundle size, improves performance, and enhances security by keeping data-fetching logic and credentials on the server.
*   **Parallel Data Fetching**: When a component needs data from multiple sources, fetch it in parallel to minimize loading times.
    ```tsx
    // Fetch in parallel
    const [articles, products] = await Promise.all([
      getArticles(),
      getProducts(),
    ]);
    ```
*   **Streaming with Suspense**: Use `Suspense` to create loading UI boundaries. This allows you to stream parts of the page to the user as they are rendered, improving perceived performance.
*   **Type-Safe API Routes**: When creating API routes, use TypeScript to define types for your request and response bodies to ensure type safety across your application.

### 5. Performance Optimization

*   **Image Optimization**: Always use the `next/image` component. It provides automatic optimization, responsive sizing, and modern format support (like WebP). Use the `priority` prop for images in the LCP (Largest Contentful Paint) element.
*   **Code Splitting with Dynamic Imports**: Use `next/dynamic` to lazy-load components that are not needed for the initial page view (e.g., modals, components below the fold).
*   **Bundle Analysis**: Use `@next/bundle-analyzer` to inspect your JavaScript bundles. This helps identify large dependencies that could be optimized or replaced.
*   **Caching Strategies**:
    *   **SSG (Static Site Generation)**: Use for pages that can be pre-rendered at build time (e.g., marketing pages, blog posts).
    *   **ISR (Incremental Static Regeneration)**: Use for pages that are mostly static but need to be updated periodically.
    *   **SSR (Server-Side Rendering)**: Use for pages that require fresh data on every request.
    *   **Client-Side Caching**: Use libraries like SWR or React Query for caching data on the client, reducing redundant API calls.

### 6. Common Pitfalls to Avoid

*   **Ignoring TypeScript Errors**: Don't ignore TypeScript errors. Address them as they appear to prevent bugs later.
*   **Large Component Trees**: Break down large components into smaller, more manageable ones. This improves readability, reusability, and performance.
*   **Prop Drilling**: Avoid passing props down through many levels of components. Use React Context or a state management library (like Zustand or Redux) for state that needs to be accessed by many components.

---

## Part 3: Project-Specific Recommendations

Based on the analysis of the `src/frontend/app` structure, here are specific recommendations for improving the application's UI, UX, and codebase.

### 1. UI/UX Enhancements

*   **Adopt a Component Library**: The project relies on custom components and likely custom CSS. Adopting a headless component library like **shadcn/ui**, which is built on **Radix UI** and **Tailwind CSS**, can dramatically improve UI consistency, accessibility, and development speed.
    *   **Action Plan**:
        1.  Integrate `shadcn/ui` into the project.
        2.  Incrementally replace existing custom components (buttons, modals, inputs) with their `shadcn/ui` equivalents.
        3.  Use its theming capabilities to create a consistent visual identity.

*   **Improve Data Visualization**: Since the application is data-heavy (experiments, datasets), presenting data effectively is crucial.
    *   **Action Plan**:
        1.  Replace standard HTML tables with a more powerful table component like **TanStack Table**. It provides out-of-the-box sorting, filtering, and pagination.
        2.  For data charts and graphs, consider using a library like **Recharts** or **Visx**.

*   **Enhance Loading States**: The presence of a `skeletons` directory is good. This can be taken further.
    *   **Action Plan**:
        1.  Implement skeleton loaders for all major data-fetching components (e.g., the tables in the `experiments` pages).
        2.  Combine this with Next.js `Suspense` to create a non-blocking loading experience, showing parts of the UI that are ready while data-heavy parts are still loading.

### 2. Code and Architecture Improvements

*   **Advanced State Management**: The `contexts` folder suggests the use of React Context. For complex, app-wide state, this can lead to performance issues due to unnecessary re-renders.
    *   **Action Plan**:
        1.  For simple, localized state, continue using `useState` and `useReducer`.
        2.  For complex shared state (e.g., user session, filters that affect multiple components), evaluate a lightweight state management library like **Zustand**. It's less boilerplate than Redux and avoids the performance pitfalls of a single large context.

*   **Efficient Data Fetching & Caching**:
    *   **Action Plan**:
        1.  Integrate **TanStack Query (React Query)** or **SWR** for client-side data fetching. These libraries provide robust caching, revalidation, and optimistic UI updates, which would be highly beneficial for the interactive tables and lists in the app.
        2.  This would also simplify the data-fetching logic within Client Components, removing the need for manual `useEffect` and `useState` combinations to handle loading, error, and data states.

*   **Component Colocation and Organization**: The structure is good, but can be more granular.
    *   **Action Plan**:
        1.  For pages with many specific components (like `.../[experiment_id]/page.tsx`), keep those components inside the `components` folder of that route (`.../[experiment_id]/components/`). This is the current approach and should be maintained.
        2.  For components that are truly reusable across different major routes (e.g., a generic `Button` or `Card`), move them to the top-level `src/frontend/app/components/ui` directory, as suggested in the best practices.

*   **Leverage Server Components More**:
    *   **Action Plan**:
        1.  Audit the Client Components (`"use client"`). Identify any that don't strictly require user interactivity or browser-only APIs.
        2.  Refactor these components to be Server Components. Fetch data in the Server Component and pass it down as props to the necessary Client Components. This reduces the client-side JavaScript bundle size.

