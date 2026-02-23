# Initial Tech Stack

Purpose: This report serves as guidance and to provide a 'minimum' standard.


## Overview

- Using newer packages than the one listed is always approved.
- If you intend on using an older version, then approval is required from Arman.
- Improvements to the stack are welcome and appreciated, but require authorization from Arman
    - Remove unused or unnecessary packages (with prior approval)
    - Change packages with newer versions, better versions, etc. (with prior approval)


## Prepared Research

As a Tech Stack Research Specialist, I have systematically verified the latest stable release versions and official documentation for your requested architecture.

### **Research Summary & Version Status (as of February 23, 2026)**

The stack is in a highly stable, "modern-standard" state. Key shifts since early 2025 include:

- **Tailwind CSS v4.x** is now the production standard, utilizing a CSS-first configuration.
- **Framer Motion** has rebranded to **Motion**, becoming framework-agnostic while maintaining first-class React support.
- **shadcn/ui** has moved to a unified `radix-ui` package, significantly cleaning up `package.json` dependencies.
- **React Router v7** is the stable successor to both v6 and Remix, introducing "Framework Mode" for Vite users.

---

### **Core Foundation**

| Technology       | Minimum Version | Locked Version (this project) | Official Documentation                               | Notes                                             |
| ---------------- | --------------- | ----------------------------- | ---------------------------------------------------- | ------------------------------------------------- |
| **React**        | `19.0.x`        | `19.0.0`                      | [react.dev](https://react.dev)                       | Standard for modern hooks/actions.                |
| **TypeScript**   | `5.7.x`         | `5.9.x` ✦                     | [typescriptlang.org](https://www.typescriptlang.org) | v6.0 is in early preview/beta for 2026.           |
| **Tailwind CSS** | `4.0.x`         | `4.2.x` ✦                     | [tailwindcss.com](https://tailwindcss.com)           | CSS-first config; no `tailwind.config.js` needed. |


### **Data Layer & Forms**

| Technology          | Minimum Version | Locked Version (this project) | Official Documentation                               | Notes                                           |
| ------------------- | --------------- | ----------------------------- | ---------------------------------------------------- | ----------------------------------------------- |
| **TanStack Query**  | `5.66.x`        | `5.90.x` ✦                    | [tanstack.com/query](https://tanstack.com/query)     | v6 exists for Svelte; React remains on v5 core. |
| **Zustand**         | `5.0.11`        | `5.0.x`                       | [zustand-demo.pmnd.rs](https://zustand-demo.pmnd.rs) | Stable v5 focus on better TS and SSR.           |
| **React Hook Form** | `7.54.x`        | `7.54.x`                      | [react-hook-form.com](https://react-hook-form.com)   | Industry standard for performant forms.         |
| **Zod**             | `3.24.x`        | `3.24.x`                      | [zod.dev](https://zod.dev)                           | Primary schema validation tool.                 |


### **UI, Tables & Animation**

| Technology         | Minimum Version | Locked Version (this project) | Official Documentation                           | Notes                                            |
| ------------------ | --------------- | ----------------------------- | ------------------------------------------------ | ------------------------------------------------ |
| **shadcn/ui**      | `2026.02` (CLI) | `2026.02` (CLI)               | [ui.shadcn.com](https://ui.shadcn.com)           | Now uses unified `radix-ui` package.             |
| **Radix UI**       | `1.1.x`         | transitive via shadcn         | [radix-ui.com](https://www.radix-ui.com)         | Installed as transitive dep by shadcn CLI.       |
| **TanStack Table** | `8.21.x`        | not yet installed             | [tanstack.com/table](https://tanstack.com/table) | Needed for run history and step_runs data grids. |
| **Motion**         | `12.3.x`        | `12.3.x`                      | [motion.dev](https://motion.dev)                 | Rebranded from Framer Motion.                    |
| **date-fns**       | `4.1.0`         | `4.1.0`                       | [date-fns.org](https://date-fns.org)             | v4 features first-class time zone support.       |


### **Dev Tools**

| Technology            | Minimum Version | Locked Version (this project) | Official Documentation                                                                             | Notes                                     |
| --------------------- | --------------- | ----------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **Biome**             | `1.9.x`         | `1.9.x`                       | [biomejs.dev](https://biomejs.dev)                                                                 | Replaces Prettier/ESLint for high speed.  |
| **TanStack DevTools** | `5.66.x`        | `5.90.x` ✦                    | [tanstack.com/query/.../devtools](https://tanstack.com/query/latest/docs/framework/react/devtools) | Installed as `@tanstack/query-devtools`.  |
| **Vitest**            | `2.0.x`         | `2.0.x`                       | [vitest.dev](https://vitest.dev)                                                                   | Test runner for Vite. Required by spec.   |


### **Routing**

| Technology       | Minimum Version | Locked Version (this project) | Official Documentation                     | Notes                                       |
| ---------------- | --------------- | ----------------------------- | ------------------------------------------ | ------------------------------------------- |
| **React Router** | `7.x`           | `7.13.x` ✦                    | [reactrouter.com](https://reactrouter.com) | Merged with Remix; current stable for Vite. |


---

✦ = Project locked version exceeds research minimum — approved.

---

### **Critical Implementation Notes for 2026**

1. **Tailwind CSS v4:** You no longer need `postcss.config.js` or a JavaScript-based `tailwind.config.js`. Import Tailwind directly in CSS: `@import "tailwindcss";`.
2. **shadcn/ui:** Components are copy-pasted via CLI — no runtime package entry. Run `npx shadcn@latest add <component>` to add. The unified `radix-ui` dep installs automatically.
3. **React Router v7:** SPA mode via `BrowserRouter` is the correct choice for this project. Framework Mode (loaders/actions) is a Next.js-style pattern and is not used here.
4. **Zod + React Hook Form:** Use `zodResolver` from `@hookform/resolvers/zod` to connect the two. Define schemas in `src/schemas/` per step type.
