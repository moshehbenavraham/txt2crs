/**
 * EXAMPLE: Compose the canonical course-submission boundary
 *
 * PATTERN: Feature hook composition, not a second mutation
 * USE WHEN: Wiring a validated prompt, text, URL, YouTube, or file form
 * TAGS: mutation, jobs, idempotency, generated-client, course-intake
 *
 * Course submission has more lifecycle rules than a generic mutation:
 * duplicate triggers share one in-flight request, an exact failed retry keeps
 * its idempotency key, changed input rotates that key, uploads use the
 * generated multipart call, and accepted IDs drive typed navigation.
 * `useCourseSubmission` owns all of those rules and the reviewed error toast.
 */

import { useCourseSubmission } from "@/hooks/useCourseSubmission"
import type { CourseIntakeValues } from "@/lib/schemas"

export interface CourseSubmissionAction {
  submit: (values: CourseIntakeValues) => void
  isSubmitting: boolean
  inlineError: string | null
}

/**
 * Adapt the product hook to a small form-facing interface.
 *
 * Do not generate or persist an idempotency key in the component. Do not call
 * `JobsService` directly here; doing either would split the reviewed retry
 * behavior across two owners.
 */
export function useCourseSubmissionAction(): CourseSubmissionAction {
  const { submitCourse, isSubmitting, submissionErrorMessage } =
    useCourseSubmission()

  return {
    submit: submitCourse,
    isSubmitting,
    inlineError: submissionErrorMessage,
  }
}

// Form composition:
//
// const submission = useCourseSubmissionAction()
// form.handleSubmit(submission.submit)
// submission.isSubmitting -> disable every mutable intake control
// submission.inlineError  -> render beside the primary action with role=alert
//
// The hook navigates to `/jobs/$jobId` only after durable server acceptance.

export default useCourseSubmissionAction
