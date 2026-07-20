import type {
  JobInputPublic,
  JobProgressPublic,
  JobProgressStage,
  JobStatusPublic,
} from "@/client"

type ProductStageId = Exclude<JobProgressStage, "failed" | "cancelled">

export type ProductStageState = "complete" | "active" | "upcoming" | "inactive"

interface ProductStageDefinition {
  id: ProductStageId
  label: string
  description: string
}

export interface ProductStagePresentation extends ProductStageDefinition {
  state: ProductStageState
}

export interface JobProgressPresentation {
  kind: "active" | "completed" | "failed" | "cancelled"
  heading: string
  stages: ProductStagePresentation[]
}

export interface InputWarningsPresentation {
  warnings: string[]
  hasAdditionalWarnings: boolean
}

const productStageDefinitions: readonly ProductStageDefinition[] = [
  {
    id: "queued",
    label: "Source accepted",
    description: "Private request admission and queueing.",
  },
  {
    id: "researching",
    label: "Research",
    description: "Source research and evidence collection.",
  },
  {
    id: "drafting",
    label: "Course drafting",
    description: "Curriculum design and module drafting.",
  },
  {
    id: "validating",
    label: "Quality checks",
    description: "Course, review, and assessment alignment.",
  },
  {
    id: "rendering",
    label: "Publication formats",
    description: "Learning-material format rendering.",
  },
  {
    id: "delivering",
    label: "Private delivery",
    description: "Owner-scoped file verification and delivery.",
  },
  {
    id: "ready",
    label: "Materials ready",
    description: "The complete learning package is available.",
  },
] as const

function getPresentationKind(
  status: JobStatusPublic["status"],
): JobProgressPresentation["kind"] {
  switch (status) {
    case "accepted":
    case "researching":
    case "drafting":
    case "validating":
    case "rendering":
    case "delivering":
      return "active"
    case "completed":
      return "completed"
    case "failed":
      return "failed"
    case "cancelled":
      return "cancelled"
    default: {
      const exhaustiveStatus: never = status
      return exhaustiveStatus
    }
  }
}

function getHeading(kind: JobProgressPresentation["kind"]): string {
  switch (kind) {
    case "active":
      return "Building your learning package"
    case "completed":
      return "Course materials are ready"
    case "failed":
      return "Course generation stopped"
    case "cancelled":
      return "Course generation cancelled"
    default: {
      const exhaustiveKind: never = kind
      return exhaustiveKind
    }
  }
}

function buildStageStates(
  kind: JobProgressPresentation["kind"],
  currentStage: JobProgressStage,
): ProductStagePresentation[] {
  if (kind === "failed" || kind === "cancelled") {
    // The public terminal response intentionally does not expose the private
    // checkpoint that failed. Neutral stages avoid claiming work completed.
    return productStageDefinitions.map((definition) => ({
      ...definition,
      state: "inactive",
    }))
  }
  if (kind === "completed") {
    return productStageDefinitions.map((definition) => ({
      ...definition,
      state: "complete",
    }))
  }

  const currentStageIndex = productStageDefinitions.findIndex(
    (definition) => definition.id === currentStage,
  )
  return productStageDefinitions.map((definition, stageIndex) => ({
    ...definition,
    state:
      stageIndex < currentStageIndex
        ? "complete"
        : stageIndex === currentStageIndex
          ? "active"
          : "upcoming",
  }))
}

/** Map only generated status/stage values into stable learner-facing copy. */
export function buildJobProgressPresentation(
  snapshot: JobStatusPublic,
): JobProgressPresentation {
  const kind = getPresentationKind(snapshot.status)
  return {
    kind,
    heading: getHeading(kind),
    stages: buildStageStates(kind, snapshot.progress.stage),
  }
}

/** Describe units without calculating a potentially misleading percentage. */
export function getProgressUnitsLabel(
  progress: Pick<JobProgressPublic, "completed_units" | "total_units">,
): string {
  if (progress.total_units === null || progress.total_units === undefined) {
    return `${progress.completed_units.toLocaleString()} course-building steps confirmed`
  }
  return `${progress.completed_units.toLocaleString()} of ${progress.total_units.toLocaleString()} course-building steps confirmed`
}

/**
 * Preserve the backend's bounded extraction notes without inventing details.
 *
 * A truncated flag can remain meaningful even when the bounded public list is
 * empty, so either public signal is enough to render the source note.
 */
export function getInputWarningsPresentation(
  input: Pick<JobInputPublic, "extraction_warnings" | "warnings_truncated">,
): InputWarningsPresentation | null {
  if (input.extraction_warnings.length === 0 && !input.warnings_truncated) {
    return null
  }
  return {
    warnings: input.extraction_warnings,
    hasAdditionalWarnings: input.warnings_truncated,
  }
}
