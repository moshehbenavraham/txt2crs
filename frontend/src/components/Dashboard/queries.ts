import { ItemsService, UsersService } from "@/client"

/**
 * The dashboard preview shows a small stable subset of the library. The API
 * documents no recency order, so this is labeled a preview, never "recent".
 */
export const DASHBOARD_PREVIEW_LIMIT = 5

export function getDashboardItemsQueryOptions() {
  return {
    queryFn: () =>
      ItemsService.readItems({
        query: { skip: 0, limit: DASHBOARD_PREVIEW_LIMIT },
      }),
    queryKey: ["items", { view: "dashboard" }],
  }
}

export function getDashboardUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ query: { skip: 0, limit: 1 } }),
    queryKey: ["users", { view: "dashboard" }],
  }
}
