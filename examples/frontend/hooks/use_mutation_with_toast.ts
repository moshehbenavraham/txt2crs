/**
 * EXAMPLE: Submit a course job with TanStack Query and toast feedback
 *
 * PATTERN: Mutation with an explicit idempotency key
 * USE WHEN: Sending a prompt, URL, text source, or file-backed request
 * TAGS: mutation, toast, tanstack-query, jobs, idempotency
 *
 * Based on the current `/api/v1/jobs` generated client contract.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import {
  type JobAcceptedPublic,
  type JobSubmissionRequest,
  JobsService,
} from "@/client"
import { handleError } from "@/utils"

import { jobKeys } from "./use_query_with_suspense"

/**
 * Keep the request and its retry key together.
 *
 * A caller must reuse the same idempotency key only when retrying the exact
 * same logical submission. A changed prompt or preference needs a new key.
 */
export interface SubmitCourseVariables {
  request: JobSubmissionRequest
  idempotencyKey: string
}

/**
 * Submit one JSON-backed course request.
 *
 * @example
 * ```tsx
 * const submitCourse = useSubmitCourse()
 *
 * submitCourse.mutate({
 *   idempotencyKey: crypto.randomUUID(),
 *   request: {
 *     consent_to_ai_processing: true,
 *     learner_age_group: "adult",
 *     preferences: {
 *       level: "beginner",
 *       audience: null,
 *       prior_knowledge: null,
 *       learning_goals: [],
 *       language: "en",
 *     },
 *     input: { type: "prompt", value: "Teach me the basics of photosynthesis" },
 *   },
 * })
 * ```
 */
export function useSubmitCourse() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ request, idempotencyKey }: SubmitCourseVariables) =>
      JobsService.submitJob({
        body: request,
        headers: {
          "Idempotency-Key": idempotencyKey,
        },
      }),

    onSuccess: (acceptedJob: JobAcceptedPublic) => {
      // Seed the accepted state only if a route already reads this key. The
      // canonical status endpoint will supply the richer polling projection.
      queryClient.invalidateQueries({
        queryKey: jobKeys.detail(acceptedJob.job_id),
      })

      toast.success("Course request accepted", {
        description: "Research and generation can now begin.",
      })
    },

    onError: (error: Error) => {
      // The shared handler translates generated client errors into the
      // application's reviewed, learner-safe message.
      handleError(error)
    },
  })
}

// Mutation-state example:
//
// const mutation = useSubmitCourse()
// mutation.isPending  -> disable duplicate submit controls
// mutation.isError    -> retain form input so the learner can retry
// mutation.isSuccess  -> navigate using mutation.data.job_id
//
// Use `mutateAsync` only when the caller must sequence navigation or another
// action after the server durably accepts the job.

export default useSubmitCourse
