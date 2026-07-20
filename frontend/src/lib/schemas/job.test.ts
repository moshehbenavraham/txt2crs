import { describe, expect, it } from "vitest"

import {
  buildJobSubmissionPayload,
  courseIntakeSchema,
  createDefaultCourseIntakeValues,
} from "./job"

const validPromptValues = {
  ...createDefaultCourseIntakeValues(),
  inputMode: "prompt" as const,
  sourceValue: "Teach the foundations of marine food webs.",
  learningGoals: ["Explain how energy moves through a marine food web."],
  learnerAgeGroup: "adult" as const,
  consentToAiProcessing: true,
}

describe("course intake contract", () => {
  it("accepts the exact learner-selectable prompt fields", () => {
    const parsed = courseIntakeSchema.parse(validPromptValues)
    const payload = buildJobSubmissionPayload(parsed)

    expect(payload).toEqual({
      kind: "json",
      body: {
        input: {
          type: "prompt",
          value: "Teach the foundations of marine food webs.",
        },
        preferences: {
          level: "auto",
          audience: null,
          prior_knowledge: null,
          learning_goals: [
            "Explain how energy moves through a marine food web.",
          ],
          language: "auto",
        },
        consent_to_ai_processing: true,
        learner_age_group: "adult",
      },
    })
  })

  it.each([
    ["text", "A complete pasted lesson source."],
    ["url", "https://example.org/course-source"],
    ["youtube", "https://www.youtube.com/watch?v=course123"],
  ] as const)(
    "builds the exact generated JSON request for a valid %s source",
    (inputMode, sourceValue) => {
      const parsed = courseIntakeSchema.parse({
        ...validPromptValues,
        inputMode,
        sourceValue,
      })
      const payload = buildJobSubmissionPayload(parsed)

      expect(payload.kind).toBe("json")
      if (payload.kind !== "json") {
        throw new Error("Expected a JSON course request.")
      }
      expect(payload.body.input).toEqual({
        type: inputMode,
        value: sourceValue,
      })
    },
  )

  it.each([
    ["prompt", "ab"],
    ["prompt", "x".repeat(10_001)],
    ["text", ""],
    ["text", "x".repeat(200_001)],
    ["url", "http://example.com"],
    ["url", "https://user:secret@example.com/course"],
    ["url", "https://example.com/course#private"],
    ["youtube", "not-a-url"],
  ] as const)("rejects an invalid %s source", (inputMode, sourceValue) => {
    const result = courseIntakeSchema.safeParse({
      ...validPromptValues,
      inputMode,
      sourceValue,
    })

    expect(result.success).toBe(false)
  })

  it("requires exact consent and at most ten case-insensitively unique goals", () => {
    expect(
      courseIntakeSchema.safeParse({
        ...validPromptValues,
        consentToAiProcessing: false,
      }).success,
    ).toBe(false)
    expect(
      courseIntakeSchema.safeParse({
        ...validPromptValues,
        learningGoals: Array.from(
          { length: 11 },
          (_, index) => `Explain objective ${index}`,
        ),
      }).success,
    ).toBe(false)
    expect(
      courseIntakeSchema.safeParse({
        ...validPromptValues,
        learningGoals: ["Explain indexing", "  explain INDEXING  "],
      }).success,
    ).toBe(false)
  })

  it("treats an untouched blank goal row as an optional empty goal list", () => {
    const parsed = courseIntakeSchema.parse({
      ...validPromptValues,
      learningGoals: [""],
    })
    const payload = buildJobSubmissionPayload(parsed)

    expect(payload.kind).toBe("json")
    if (payload.kind !== "json") {
      throw new Error("Expected a JSON course request.")
    }
    expect(payload.body.preferences.learning_goals).toEqual([])
  })

  it("strips inactive source fields and serializes one upload metadata part", () => {
    const file = new File(["%PDF-1.7 test"], "course.pdf", {
      type: "application/pdf",
    })
    const parsed = courseIntakeSchema.parse({
      ...validPromptValues,
      inputMode: "upload",
      sourceValue: "private stale prompt",
      sourceFile: file,
    })
    const payload = buildJobSubmissionPayload(parsed)

    expect(payload.kind).toBe("upload")
    if (payload.kind !== "upload") {
      throw new Error("Expected upload payload.")
    }
    expect(payload.file).toBe(file)
    expect(JSON.parse(payload.metadata)).toEqual({
      preferences: {
        level: "auto",
        audience: null,
        prior_knowledge: null,
        learning_goals: ["Explain how energy moves through a marine food web."],
        language: "auto",
      },
      consent_to_ai_processing: true,
      learner_age_group: "adult",
    })
    expect(payload.metadata).not.toContain("private stale prompt")
  })

  it.each([
    ["course.pdf", "application/pdf"],
    [
      "course.docx",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
    [
      "course.pptx",
      "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ],
  ] as const)(
    "accepts a matching %s upload without reading its bytes",
    (fileName, mediaType) => {
      const file = new File(["bounded fixture"], fileName, { type: mediaType })
      const parsed = courseIntakeSchema.parse({
        ...validPromptValues,
        inputMode: "upload",
        sourceFile: file,
      })
      const payload = buildJobSubmissionPayload(parsed)

      expect(payload.kind).toBe("upload")
      if (payload.kind !== "upload") {
        throw new Error("Expected an upload course request.")
      }
      expect(payload.file).toBe(file)
      expect(payload.metadata).not.toContain("bounded fixture")
    },
  )
})
