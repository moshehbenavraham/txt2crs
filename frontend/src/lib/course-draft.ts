/**
 * Bounded session-only prompt handoff between public access and `/create`.
 *
 * Drafts never enter URLs, localStorage, logs, or the API. Every read parses a
 * versioned strict envelope and revalidates the prompt before returning it.
 */
import { z } from "zod"
import { coursePromptField } from "@/lib/schemas"

export const COURSE_PROMPT_DRAFT_STORAGE_KEY = "txt2crs.coursePromptDraft.v1"

// A maximum prompt serializes to just over 10,000 characters. This small
// framing allowance lets us reject an oversized/corrupt value before JSON
// parsing or schema allocation.
const MAXIMUM_SERIALIZED_DRAFT_CHARACTERS = 10_128

const coursePromptDraftSchema = z
  .object({
    version: z.literal(1),
    prompt: coursePromptField,
  })
  .strict()

function getSessionStorageSafely(): Storage | null {
  // Access itself can throw in sandboxed/private browser contexts.
  try {
    return typeof window === "undefined" ? null : window.sessionStorage
  } catch {
    return null
  }
}

function resolveStorage(storage: Storage | undefined): Storage | null {
  return storage ?? getSessionStorageSafely()
}

/** Remove the draft without surfacing browser storage errors. */
export function clearCoursePromptDraft(storage?: Storage): void {
  try {
    resolveStorage(storage)?.removeItem(COURSE_PROMPT_DRAFT_STORAGE_KEY)
  } catch {
    // Storage denial is already the safe no-draft outcome.
  }
}

/**
 * Save one valid prompt in this tab only.
 *
 * Invalid replacement input clears any older valid draft so a stale prompt
 * cannot unexpectedly survive a learner's newer edit.
 */
export function saveCoursePromptDraft(
  prompt: string,
  storage?: Storage,
): boolean {
  const promptResult = coursePromptField.safeParse(prompt)
  if (!promptResult.success) {
    clearCoursePromptDraft(storage)
    return false
  }

  const serializedDraft = JSON.stringify({
    version: 1,
    prompt: promptResult.data,
  })
  if (serializedDraft.length > MAXIMUM_SERIALIZED_DRAFT_CHARACTERS) {
    clearCoursePromptDraft(storage)
    return false
  }

  try {
    const resolvedStorage = resolveStorage(storage)
    if (resolvedStorage === null) {
      return false
    }
    resolvedStorage.setItem(COURSE_PROMPT_DRAFT_STORAGE_KEY, serializedDraft)
    return true
  } catch {
    return false
  }
}

/** Read and revalidate a prompt; corrupt or stale data is cleared immediately. */
export function readCoursePromptDraft(storage?: Storage): string | null {
  let rawDraft: string | null
  try {
    const resolvedStorage = resolveStorage(storage)
    if (resolvedStorage === null) {
      return null
    }
    rawDraft = resolvedStorage.getItem(COURSE_PROMPT_DRAFT_STORAGE_KEY)
  } catch {
    return null
  }

  if (rawDraft === null) {
    return null
  }
  if (rawDraft.length > MAXIMUM_SERIALIZED_DRAFT_CHARACTERS) {
    clearCoursePromptDraft(storage)
    return null
  }

  let parsedJson: unknown
  try {
    parsedJson = JSON.parse(rawDraft)
  } catch {
    clearCoursePromptDraft(storage)
    return null
  }
  const parsedDraft = coursePromptDraftSchema.safeParse(parsedJson)
  if (!parsedDraft.success) {
    clearCoursePromptDraft(storage)
    return null
  }
  return parsedDraft.data.prompt
}

/** Read once and clear even when the persisted value is invalid. */
export function consumeCoursePromptDraft(storage?: Storage): string | null {
  const prompt = readCoursePromptDraft(storage)
  clearCoursePromptDraft(storage)
  return prompt
}
