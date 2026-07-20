import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useRef } from "react"

import {
  type BodyJobsSubmitJobUpload,
  type JobAcceptedPublic,
  type JobSubmissionRequest,
  JobsService,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { ApiError, getApiErrorMessage } from "@/lib/api-error"
import {
  buildJobSubmissionPayload,
  type CourseIntakeValues,
  type CourseSubmissionPayload,
} from "@/lib/schemas"
import { asJobId, createIdempotencyKey, type IdempotencyKey } from "@/lib/types"

type IdempotencyHeader = {
  "Idempotency-Key": IdempotencyKey
}

export interface CourseSubmissionTransport {
  submitJson: (options: {
    body: JobSubmissionRequest
    headers: IdempotencyHeader
  }) => Promise<JobAcceptedPublic>
  submitUpload: (options: {
    body: BodyJobsSubmitJobUpload
    headers: IdempotencyHeader
  }) => Promise<JobAcceptedPublic>
}

interface CourseSubmissionCoordinatorOptions {
  transport?: CourseSubmissionTransport
  createKey?: () => IdempotencyKey
}

export interface CourseSubmissionCoordinator {
  isInFlight: () => boolean
  submit: (values: CourseIntakeValues) => Promise<JobAcceptedPublic>
}

const genericSubmissionError =
  "The course request could not be accepted. Try again."

const generatedClientTransport: CourseSubmissionTransport = {
  submitJson: (options) => JobsService.submitJob(options),
  submitUpload: (options) => JobsService.submitJobUpload(options),
}

function createSecureSubmissionKey(): IdempotencyKey {
  const randomUuid = globalThis.crypto?.randomUUID()
  if (!randomUuid) {
    throw new Error("Secure course submission identity is unavailable.")
  }
  return createIdempotencyKey(`course-${randomUuid}`)
}

/**
 * Return only reviewed API Problem Details text.
 *
 * Unknown JavaScript errors and transport failures may contain browser,
 * request, or implementation detail, so they collapse to one fixed recovery
 * message. Backend `ApiError` detail is bounded before reaching the learner.
 */
export function getCourseSubmissionErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError) || error.status === 0) {
    return genericSubmissionError
  }

  const problemDetail = getApiErrorMessage(error).trim()
  return problemDetail.length > 0 && problemDetail.length <= 500
    ? problemDetail
    : genericSubmissionError
}

/**
 * Create a canonical identity without logging or persistently storing content.
 *
 * JSON values are already trimmed and transformed by Zod, so their generated
 * request has deterministic property order. The bounded canonical string
 * exists only inside this mounted coordinator. Upload bytes are deliberately
 * not read; a WeakMap gives the selected File object a stable, in-memory-only
 * identity for exact retries and rotates when it is replaced.
 */
function createCanonicalDraftFactory() {
  const selectedFileIdentities = new WeakMap<File, string>()
  let nextSelectedFileIdentity = 1

  return (payload: CourseSubmissionPayload): string => {
    if (payload.kind === "json") {
      return JSON.stringify(["json", payload.body])
    }

    let fileIdentity = selectedFileIdentities.get(payload.file)
    if (!fileIdentity) {
      fileIdentity = `selected-file-${nextSelectedFileIdentity}`
      nextSelectedFileIdentity += 1
      selectedFileIdentities.set(payload.file, fileIdentity)
    }
    return JSON.stringify([
      "upload",
      payload.metadata,
      payload.file.name,
      payload.file.type,
      payload.file.size,
      payload.file.lastModified,
      fileIdentity,
    ])
  }
}

/**
 * Own retry-key and duplicate-trigger lifecycle independently of React.
 *
 * A failed exact retry retains its key. Changing the canonical draft replaces
 * the key, and a successful durable acceptance clears it so any later course
 * starts with a fresh identity.
 */
export function createCourseSubmissionCoordinator({
  transport = generatedClientTransport,
  createKey = createSecureSubmissionKey,
}: CourseSubmissionCoordinatorOptions = {}): CourseSubmissionCoordinator {
  const createCanonicalDraft = createCanonicalDraftFactory()
  let activeCanonicalDraft: string | null = null
  let activeIdempotencyKey: IdempotencyKey | null = null
  let inFlightRequest: Promise<JobAcceptedPublic> | null = null

  const submit = (values: CourseIntakeValues): Promise<JobAcceptedPublic> => {
    const payload = buildJobSubmissionPayload(values)
    const canonicalDraft = createCanonicalDraft(payload)

    if (inFlightRequest !== null) {
      if (canonicalDraft === activeCanonicalDraft) {
        return inFlightRequest
      }
      return Promise.reject(
        new Error("A course submission is already in progress."),
      )
    }

    if (
      activeCanonicalDraft !== canonicalDraft ||
      activeIdempotencyKey === null
    ) {
      activeCanonicalDraft = canonicalDraft
      activeIdempotencyKey = createKey()
    }

    const headers: IdempotencyHeader = {
      "Idempotency-Key": activeIdempotencyKey,
    }
    const request =
      payload.kind === "json"
        ? transport.submitJson({ body: payload.body, headers })
        : transport.submitUpload({
            body: { file: payload.file, metadata: payload.metadata },
            headers,
          })

    inFlightRequest = request.then(
      (acceptedJob) => {
        // Durable acceptance completed. A future submission must use a new
        // owner-scoped identity even when the learner later repeats the topic.
        activeCanonicalDraft = null
        activeIdempotencyKey = null
        inFlightRequest = null
        return acceptedJob
      },
      (error: unknown) => {
        // Keep canonical draft and key for an exact retry, but release the
        // single-flight lock so the learner can act on the safe error.
        inFlightRequest = null
        throw error
      },
    )
    return inFlightRequest
  }

  return {
    isInFlight: () => inFlightRequest !== null,
    submit,
  }
}

/** Connect the strict intake form to the generated client and private route. */
export function useCourseSubmission() {
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()
  const coordinatorRef = useRef<CourseSubmissionCoordinator | null>(null)
  if (coordinatorRef.current === null) {
    coordinatorRef.current = createCourseSubmissionCoordinator()
  }
  const coordinator = coordinatorRef.current

  const submissionMutation = useMutation({
    mutationFn: (values: CourseIntakeValues) => coordinator.submit(values),
    onSuccess: (acceptedJob) => {
      // The generated response is backend-validated. Navigate from its opaque
      // identity rather than trusting or parsing the returned status URL.
      const acceptedJobId = asJobId(acceptedJob.job_id)
      navigate({
        to: "/jobs/$jobId",
        params: { jobId: acceptedJobId },
      })
    },
    onError: (error: unknown) => {
      showErrorToast(getCourseSubmissionErrorMessage(error))
    },
  })

  const submitCourse = (values: CourseIntakeValues) => {
    // This synchronous single-flight check closes the small gap before
    // TanStack publishes `isPending` to the next React render.
    if (submissionMutation.isPending || coordinator.isInFlight()) {
      return
    }
    submissionMutation.mutate(values)
  }

  return {
    submitCourse,
    isSubmitting: submissionMutation.isPending,
    submissionErrorMessage: submissionMutation.error
      ? getCourseSubmissionErrorMessage(submissionMutation.error)
      : null,
  }
}
