/**
 * EXAMPLE: TanStack Query ownership for users and course progress
 *
 * PATTERN: Suspense query with the generated API client
 * USE WHEN: A routed component cannot render until its server state is ready
 * TAGS: query, suspense, tanstack-query, jobs, data-fetching
 *
 * The production client is generated from OpenAPI. Never recreate response
 * types or hand-write requests that bypass it.
 */

import { useSuspenseQuery } from "@tanstack/react-query"

import type { UserPublic } from "@/client"
import { UsersService } from "@/client"
import { useJobProgressQuery } from "@/components/CourseProgress/queries"
import type { JobId } from "@/lib/types"

/**
 * Fetch the authenticated user inside an existing Suspense boundary.
 */
export function useCurrentUser() {
  const { data: user } = useSuspenseQuery<UserPublic>({
    queryKey: ["currentUser"],
    queryFn: () => UsersService.readUserMe(),
  })

  return { user }
}

/**
 * Fetch one private course job.
 *
 * The backend authorizes the job against the current user. The browser passes
 * only the opaque job ID and never caches learner content outside TanStack
 * Query's in-memory cache.
 *
 * @example
 * ```tsx
 * function CourseProgress({ jobId }: { jobId: string }) {
 *   const { job } = useCourseJob(jobId)
 *   return <p>{job.progress.message}</p>
 * }
 * ```
 */
export function useCourseJob(jobId: JobId) {
  // This reviewed feature hook deliberately uses regular `useQuery` because
  // the progress page keeps its last safe snapshot visible while reconnecting
  // and owns distinct initial, offline, failed, cancelled, and completed UI.
  return useJobProgressQuery(jobId)
}

// Key decisions:
//
// 1. Compose `useJobProgressQuery`; it owns the generated read, query key,
//    polling cadence, transient backoff, terminal stop, and revision guard.
// 2. Use Suspense when a route owns one honest fallback. Use regular queries
//    when the feature must distinguish several meaningful async states.
// 3. Do not put learner prompts, extracted content, or secrets in query keys;
//    query keys can appear in developer tooling.

export default useCurrentUser
