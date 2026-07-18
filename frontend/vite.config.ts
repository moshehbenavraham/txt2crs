import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

const chunkGroups = {
  react: ["react", "react-dom"],
  "tanstack-router": ["@tanstack/react-router"],
  "tanstack-query": ["@tanstack/react-query"],
  "tanstack-table": ["@tanstack/react-table"],
  radix: [
    "@radix-ui/react-avatar",
    "@radix-ui/react-checkbox",
    "@radix-ui/react-dialog",
    "@radix-ui/react-dropdown-menu",
    "@radix-ui/react-label",
    "@radix-ui/react-radio-group",
    "@radix-ui/react-scroll-area",
    "@radix-ui/react-select",
    "@radix-ui/react-separator",
    "@radix-ui/react-slot",
    "@radix-ui/react-tabs",
    "@radix-ui/react-tooltip",
  ],
  icons: ["lucide-react", "react-icons"],
  forms: ["react-hook-form", "@hookform/resolvers", "zod"],
} as const

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  plugins: [
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
    }),
    react(),
    tailwindcss(),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          for (const [chunkName, dependencies] of Object.entries(chunkGroups)) {
            if (
              dependencies.some((dependency) =>
                id.includes(`/node_modules/${dependency}/`),
              )
            ) {
              return chunkName
            }
          }
        },
      },
    },
  },
})
