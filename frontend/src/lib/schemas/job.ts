/**
 * Strict learner-selectable course intake and generated-client payloads.
 *
 * Form field names stay ergonomic for React Hook Form. The payload builder is
 * the single boundary that translates them into the generated snake-case API
 * contract, so components cannot accidentally send inactive or server-owned
 * values.
 */

import { z } from "zod"
import type {
  BodyJobsSubmitJobUpload,
  JobPreferences,
  JobSubmissionRequest,
} from "@/client"
import {
  courseAudienceField,
  courseConsentField,
  courseLearnerAgeGroupField,
  courseLearningGoalField,
  courseLearningLevelField,
  coursePriorKnowledgeField,
  coursePromptField,
  courseSourceFileField,
  courseSourceTextField,
  courseSourceUrlField,
} from "./fields"

const courseInputModes = ["prompt", "text", "url", "youtube", "upload"] as const

const rawCourseIntakeSchema = z
  .object({
    inputMode: z.enum(courseInputModes),
    // Both source controls exist while editing. The transform below removes
    // the inactive value after mode-specific validation succeeds.
    sourceValue: z.string().optional().default(""),
    sourceFile: z
      .custom<File | undefined>(
        (value) =>
          value === undefined ||
          (typeof File !== "undefined" && value instanceof File),
        { message: "Choose a browser file" },
      )
      .optional(),
    level: courseLearningLevelField,
    audience: courseAudienceField,
    priorKnowledge: coursePriorKnowledgeField,
    // The first empty UI row is optional. Non-empty entries receive the exact
    // LearningGoal validation below, then blank rows are removed on output.
    learningGoals: z
      .array(z.string().max(500))
      .max(10, { message: "Add at most 10 learning goals" }),
    language: z.literal("auto"),
    learnerAgeGroup: courseLearnerAgeGroupField,
    // ``false`` is a valid untouched form state but never a valid parsed
    // submission. The cross-field pass below turns it into a field error.
    consentToAiProcessing: z.union([courseConsentField, z.literal(false)]),
  })
  .strict()
  .superRefine((values, refinementContext) => {
    if (values.inputMode === "upload") {
      const fileResult = courseSourceFileField.safeParse(values.sourceFile)
      if (!fileResult.success) {
        for (const issue of fileResult.error.issues) {
          refinementContext.addIssue({
            code: "custom",
            message: issue.message,
            path: ["sourceFile"],
          })
        }
      }
    } else {
      const sourceSchema =
        values.inputMode === "prompt"
          ? coursePromptField
          : values.inputMode === "text"
            ? courseSourceTextField
            : courseSourceUrlField
      const sourceResult = sourceSchema.safeParse(values.sourceValue)
      if (!sourceResult.success) {
        for (const issue of sourceResult.error.issues) {
          refinementContext.addIssue({
            code: "custom",
            message: issue.message,
            path: ["sourceValue"],
          })
        }
      }
    }

    const nonEmptyGoals = values.learningGoals
      .map((learningGoal, goalIndex) => ({
        goalIndex,
        value: learningGoal.trim(),
      }))
      .filter((learningGoal) => learningGoal.value.length > 0)
    for (const learningGoal of nonEmptyGoals) {
      const goalResult = courseLearningGoalField.safeParse(learningGoal.value)
      if (!goalResult.success) {
        for (const issue of goalResult.error.issues) {
          refinementContext.addIssue({
            code: "custom",
            message: issue.message,
            path: ["learningGoals", learningGoal.goalIndex],
          })
        }
      }
    }
    const normalizedGoals = nonEmptyGoals.map((learningGoal) =>
      learningGoal.value.toLocaleLowerCase().replace(/\s+/g, " ").trim(),
    )
    if (new Set(normalizedGoals).size !== normalizedGoals.length) {
      refinementContext.addIssue({
        code: "custom",
        message: "Learning goals must be unique",
        path: ["learningGoals"],
      })
    }
    if (values.consentToAiProcessing !== true) {
      refinementContext.addIssue({
        code: "custom",
        message: "Allow AI and research processing to create the course",
        path: ["consentToAiProcessing"],
      })
    }
  })

/**
 * Output is a true discriminated union. Inactive source data is absent rather
 * than blanked, which protects request hashing and multipart metadata.
 */
export const courseIntakeSchema = rawCourseIntakeSchema.transform((values) => {
  const sharedValues = {
    level: values.level,
    audience: values.audience,
    priorKnowledge: values.priorKnowledge,
    learningGoals: values.learningGoals
      .map((learningGoal) => learningGoal.trim())
      .filter((learningGoal) => learningGoal.length > 0),
    language: values.language,
    learnerAgeGroup: values.learnerAgeGroup,
    // Super-refinement above proves this literal before transformation.
    consentToAiProcessing: true as const,
  }

  if (values.inputMode === "upload") {
    return {
      ...sharedValues,
      inputMode: "upload" as const,
      sourceFile: courseSourceFileField.parse(values.sourceFile),
    }
  }

  const sourceSchema =
    values.inputMode === "prompt"
      ? coursePromptField
      : values.inputMode === "text"
        ? courseSourceTextField
        : courseSourceUrlField
  return {
    ...sharedValues,
    inputMode: values.inputMode,
    sourceValue: sourceSchema.parse(values.sourceValue),
  }
})

export type CourseIntakeFormValues = z.input<typeof courseIntakeSchema>
export type CourseIntakeValues = z.output<typeof courseIntakeSchema>

export type CourseSubmissionPayload =
  | {
      kind: "json"
      body: JobSubmissionRequest
    }
  | {
      kind: "upload"
      file: File
      metadata: BodyJobsSubmitJobUpload["metadata"]
    }

/** Return an editable invalid-until-completed form with no retained source. */
export function createDefaultCourseIntakeValues(): CourseIntakeFormValues {
  return {
    inputMode: "prompt",
    sourceValue: "",
    sourceFile: undefined,
    level: "auto",
    audience: "",
    priorKnowledge: "",
    learningGoals: [""],
    language: "auto",
    learnerAgeGroup: "not_provided",
    consentToAiProcessing: false,
  }
}

function buildPreferences(values: CourseIntakeValues): JobPreferences {
  return {
    level: values.level,
    audience: values.audience || null,
    prior_knowledge: values.priorKnowledge || null,
    learning_goals: values.learningGoals,
    language: values.language,
  }
}

/** Build only one exact generated-client JSON or multipart request shape. */
export function buildJobSubmissionPayload(
  values: CourseIntakeValues,
): CourseSubmissionPayload {
  const metadata = {
    preferences: buildPreferences(values),
    consent_to_ai_processing: values.consentToAiProcessing,
    learner_age_group: values.learnerAgeGroup,
  } satisfies Omit<JobSubmissionRequest, "input">

  if (values.inputMode === "upload") {
    return {
      kind: "upload",
      file: values.sourceFile,
      metadata: JSON.stringify(metadata),
    }
  }

  return {
    kind: "json",
    body: {
      ...metadata,
      input: {
        type: values.inputMode,
        value: values.sourceValue,
      },
    },
  }
}
