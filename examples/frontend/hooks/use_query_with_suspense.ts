/**
 * EXAMPLE: TanStack Query with Suspense for owner-scoped course jobs
 *
 * PATTERN: Suspense query with the generated API client
 * USE WHEN: A routed component cannot render until its server state is ready
 * TAGS: query, suspense, tanstack-query, jobs, data-fetching
 *
 * The production client is generated from OpenAPI. Never recreate response
 * types or hand-write requests that bypass it.
 */

import { useQuery, useSuspenseQuery } from "@tanstack/react-query"

import {
  type JobStatusPublic,
  JobsService,
  type UserPublic,
  UsersService,
} from "@/client"

/**
 * Keep query keys in one small factory so reads and invalidations cannot drift.
 */
export const jobKeys = {
  all: ["jobs"] as const,
  detail: (jobId: string) => [...jobKeys.all, jobId] as const,
}

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
export function useCourseJob(jobId: string) {
  const { data: job } = useSuspenseQuery<JobStatusPublic>({
    queryKey: jobKeys.detail(jobId),
    queryFn: () =>
      JobsService.readJob({
        path: { job_id: jobId },
      }),
  })

  return { job }
}

/**
 * Use regular `useQuery` when a component owns its loading and error states.
 *
 * This form is also useful when a route may not have a job ID yet. The
 * `enabled` guard prevents a request with an empty identifier.
 */
export function useCourseJobWithoutSuspense(jobId: string | undefined) {
  const query = useQuery<JobStatusPublic>({
    queryKey: jobKeys.detail(jobId ?? "pending"),
    queryFn: () => {
      if (!jobId) {
        throw new Error("A job ID is required before reading course status.")
      }

      return JobsService.readJob({
        path: { job_id: jobId },
      })
    },
    enabled: Boolean(jobId),
  })

  return {
    job: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
  }
}

// Key decisions:
//
// 1. Put every request parameter in the query key. Different jobs must never
//    share a cache entry.
// 2. Use the generated service and response types. They remain synchronized
//    with backend validation when `npm run generate-client` runs.
// 3. Prefer Suspense when the route already owns a fallback. Prefer `useQuery`
//    when the component needs a deliberate inline loading state.
// 4. Do not put learner prompts, extracted content, or secrets in query keys;
//    query keys can appear in developer tooling.

export default useCurrentUser
