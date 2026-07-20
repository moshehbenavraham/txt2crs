import {
  createFileRoute,
  Outlet,
  redirect,
  useRouterState,
} from "@tanstack/react-router"

import { UsersService } from "@/client"
import { Logo } from "@/components/Common/Logo"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { isLoggedIn } from "@/hooks/useAuth"
import { ApiError } from "@/lib/api-error"
import {
  CURRENT_USER_QUERY_KEY,
  clearAuthSession,
  shouldInvalidateSession,
} from "@/lib/session"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async ({ context }) => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }

    // Validate token server-side by fetching the current user
    try {
      await context.queryClient.ensureQueryData({
        queryKey: CURRENT_USER_QUERY_KEY,
        queryFn: () => UsersService.readUserMe(),
      })
    } catch (error) {
      if (error instanceof ApiError && shouldInvalidateSession(error)) {
        // Token is invalid/expired - clear it and redirect to login
        clearAuthSession(context.queryClient)
        throw redirect({
          to: "/login",
        })
      }
      throw error
    }
  },
})

const SECTION_LABELS: Record<string, string> = {
  "/create": "Create course",
  "/admin": "Admin",
  "/setup": "System setup",
  "/settings": "Settings",
  "/forbidden": "Not authorized",
}

function SectionLabel() {
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  })
  const normalized =
    pathname.length > 1 && pathname.endsWith("/")
      ? pathname.slice(0, -1)
      : pathname
  const label = normalized.startsWith("/jobs/")
    ? "Course progress"
    : SECTION_LABELS[normalized]

  if (!label) {
    return null
  }

  return (
    <span className="truncate text-body-sm text-muted-foreground">{label}</span>
  )
}

function Layout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b border-border/50 px-3 md:px-4 bg-background/80 backdrop-blur-sm [view-transition-name:command-strip]">
          <SidebarTrigger className="size-11 md:size-7 -ml-1 text-muted-foreground/60 hover:text-foreground transition-colors duration-200" />
          <Logo variant="icon" className="md:hidden" />
          <SectionLabel />
        </header>
        <div className="flex-1 px-(--space-page-inline) py-6 md:py-10">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
