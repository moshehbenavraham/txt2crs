import { describe, expect, it, vi } from "vitest"

import type { JobAcceptedPublic } from "@/client"
import { ApiError } from "@/lib/api-error"
import {
  courseIntakeSchema,
  createDefaultCourseIntakeValues,
} from "@/lib/schemas"
import { asIdempotencyKey } from "@/lib/types"
import {
  type CourseSubmissionTransport,
  createCourseSubmissionCoordinator,
  getCourseSubmissionErrorMessage,
} from "./useCourseSubmission"

const acceptedJob: JobAcceptedPublic = {
  schema_version: "1.0",
  job_id: "job_test_01",
  status: "accepted",
  revision: 1,
  status_url: "/api/v1/jobs/job_test_01",
}

const parsedValidPrompt = courseIntakeSchema.parse({
  ...createDefaultCourseIntakeValues(),
  sourceValue: "Teach Python variables.",
  learningGoals: ["Explain and use Python variables."],
  learnerAgeGroup: "adult",
  consentToAiProcessing: true,
})
if (parsedValidPrompt.inputMode !== "prompt") {
  throw new Error("The prompt test fixture must stay a prompt.")
}
const validPrompt = parsedValidPrompt

function createTransport(): CourseSubmissionTransport {
  return {
    submitJson: vi.fn().mockResolvedValue(acceptedJob),
    submitUpload: vi.fn().mockResolvedValue(acceptedJob),
  }
}

describe("course submission coordinator", () => {
  it("delegates JSON requests with one generated owner-scoped key", async () => {
    const transport = createTransport()
    const coordinator = createCourseSubmissionCoordinator({
      transport,
      createKey: () => asIdempotencyKey("course-key-1"),
    })

    await expect(coordinator.submit(validPrompt)).resolves.toEqual(acceptedJob)
    expect(transport.submitJson).toHaveBeenCalledWith({
      body: expect.objectContaining({
        input: { type: "prompt", value: "Teach Python variables." },
      }),
      headers: { "Idempotency-Key": "course-key-1" },
    })
    expect(transport.submitUpload).not.toHaveBeenCalled()
  })

  it("shares one in-flight request when a learner triggers submit twice", async () => {
    let resolveRequest: (accepted: JobAcceptedPublic) => void = () => undefined
    const pendingRequest = new Promise<JobAcceptedPublic>((resolve) => {
      resolveRequest = resolve
    })
    const transport = createTransport()
    vi.mocked(transport.submitJson).mockReturnValue(pendingRequest)
    const coordinator = createCourseSubmissionCoordinator({
      transport,
      createKey: () => asIdempotencyKey("course-key-2"),
    })

    const firstRequest = coordinator.submit(validPrompt)
    const duplicateRequest = coordinator.submit(validPrompt)

    expect(duplicateRequest).toBe(firstRequest)
    expect(transport.submitJson).toHaveBeenCalledTimes(1)
    resolveRequest(acceptedJob)
    await expect(firstRequest).resolves.toEqual(acceptedJob)
  })

  it("reuses a key after failure and rotates it after change or success", async () => {
    const transport = createTransport()
    vi.mocked(transport.submitJson)
      .mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValue(acceptedJob)
    const generatedKeys = ["retry-key-1", "retry-key-2", "retry-key-3"]
    const coordinator = createCourseSubmissionCoordinator({
      transport,
      createKey: () =>
        asIdempotencyKey(generatedKeys.shift() ?? "unexpected-key"),
    })

    await expect(coordinator.submit(validPrompt)).rejects.toThrow("offline")
    await expect(coordinator.submit(validPrompt)).resolves.toEqual(acceptedJob)
    expect(vi.mocked(transport.submitJson).mock.calls[0]?.[0].headers).toEqual({
      "Idempotency-Key": "retry-key-1",
    })
    expect(vi.mocked(transport.submitJson).mock.calls[1]?.[0].headers).toEqual({
      "Idempotency-Key": "retry-key-1",
    })

    await coordinator.submit({
      ...validPrompt,
      sourceValue: "Teach Python functions.",
    })
    await coordinator.submit({
      ...validPrompt,
      sourceValue: "Teach Python functions.",
    })
    expect(vi.mocked(transport.submitJson).mock.calls[2]?.[0].headers).toEqual({
      "Idempotency-Key": "retry-key-2",
    })
    expect(vi.mocked(transport.submitJson).mock.calls[3]?.[0].headers).toEqual({
      "Idempotency-Key": "retry-key-3",
    })
  })

  it("sends multipart metadata and the original selected File", async () => {
    const selectedFile = new File(["slides"], "course.pptx", {
      type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    })
    const uploadValues = courseIntakeSchema.parse({
      ...createDefaultCourseIntakeValues(),
      inputMode: "upload",
      sourceFile: selectedFile,
      learningGoals: ["Compare the examples in the course."],
      learnerAgeGroup: "adult",
      consentToAiProcessing: true,
    })
    const transport = createTransport()
    const coordinator = createCourseSubmissionCoordinator({
      transport,
      createKey: () => asIdempotencyKey("upload-key-1"),
    })

    await coordinator.submit(uploadValues)

    expect(transport.submitUpload).toHaveBeenCalledWith({
      body: {
        file: selectedFile,
        metadata: expect.stringContaining('"consent_to_ai_processing":true'),
      },
      headers: { "Idempotency-Key": "upload-key-1" },
    })
    expect(transport.submitJson).not.toHaveBeenCalled()
  })

  it("preserves bounded RFC problem detail but hides unknown failures", () => {
    expect(
      getCourseSubmissionErrorMessage(
        new ApiError({
          body: { detail: "The course source could not be accepted." },
          status: 422,
          url: "/api/v1/jobs",
        }),
      ),
    ).toBe("The course source could not be accepted.")
    expect(
      getCourseSubmissionErrorMessage(
        new ApiError({
          body: new Error("Failed to fetch"),
          status: 0,
          url: "/api/v1/jobs",
        }),
      ),
    ).toBe("The course request could not be accepted. Try again.")
    expect(
      getCourseSubmissionErrorMessage(new Error("private stack fact")),
    ).toBe("The course request could not be accepted. Try again.")
  })
})
