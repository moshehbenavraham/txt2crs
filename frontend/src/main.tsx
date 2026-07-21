import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { client } from "./client/client.gen"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import "./index.css"
import { ApiError, createApiError } from "./lib/api-error"
import { buildLoginHref } from "./lib/auth-return"
import {
  clearAuthSession,
  getAccessToken,
  hasAccessToken,
  shouldInvalidateSession,
} from "./lib/session"
import { routeTree } from "./routeTree.gen"

client.setConfig({
  auth: () => getAccessToken() ?? undefined,
  baseUrl: import.meta.env.VITE_API_URL,
})
client.interceptors.error.use(createApiError)

const handleApiError = (error: Error) => {
  if (
    error instanceof ApiError &&
    hasAccessToken() &&
    shouldInvalidateSession(error)
  ) {
    clearAuthSession(queryClient)
    window.location.href = buildLoginHref(
      `${window.location.pathname}${window.location.search}${window.location.hash}`,
    )
  }
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({
  routeTree,
  context: { queryClient },
})
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

export type RouterContext = {
  queryClient: QueryClient
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster richColors closeButton />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
)
