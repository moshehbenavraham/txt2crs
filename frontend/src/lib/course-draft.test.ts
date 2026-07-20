import { describe, expect, it } from "vitest"
import {
  COURSE_PROMPT_DRAFT_STORAGE_KEY,
  clearCoursePromptDraft,
  consumeCoursePromptDraft,
  readCoursePromptDraft,
  saveCoursePromptDraft,
} from "./course-draft"

class MemoryStorage implements Storage {
  private readonly values = new Map<string, string>()

  get length(): number {
    return this.values.size
  }

  clear(): void {
    this.values.clear()
  }

  getItem(key: string): string | null {
    return this.values.get(key) ?? null
  }

  key(index: number): string | null {
    return [...this.values.keys()][index] ?? null
  }

  removeItem(key: string): void {
    this.values.delete(key)
  }

  setItem(key: string, value: string): void {
    this.values.set(key, value)
  }
}

describe("session-scoped prompt draft storage", () => {
  it("stores and consumes one bounded versioned prompt", () => {
    const sessionOnlyStorage = new MemoryStorage()

    expect(
      saveCoursePromptDraft(
        "  Teach marine ecology from fundamentals.  ",
        sessionOnlyStorage,
      ),
    ).toBe(true)
    expect(readCoursePromptDraft(sessionOnlyStorage)).toBe(
      "Teach marine ecology from fundamentals.",
    )
    expect(consumeCoursePromptDraft(sessionOnlyStorage)).toBe(
      "Teach marine ecology from fundamentals.",
    )
    expect(readCoursePromptDraft(sessionOnlyStorage)).toBeNull()
  })

  it.each([
    "{corrupt-json",
    JSON.stringify({ version: 2, prompt: "Teach valid content." }),
    JSON.stringify({ version: 1, prompt: "ab" }),
    "x".repeat(10_200),
  ])("clears corrupt, stale, or oversized persisted data", (rawValue) => {
    const sessionOnlyStorage = new MemoryStorage()
    sessionOnlyStorage.setItem(COURSE_PROMPT_DRAFT_STORAGE_KEY, rawValue)

    expect(readCoursePromptDraft(sessionOnlyStorage)).toBeNull()
    expect(
      sessionOnlyStorage.getItem(COURSE_PROMPT_DRAFT_STORAGE_KEY),
    ).toBeNull()
  })

  it("rejects an invalid replacement and never touches another storage area", () => {
    const sessionOnlyStorage = new MemoryStorage()
    const unrelatedPersistentStorage = new MemoryStorage()
    unrelatedPersistentStorage.setItem("unrelated", "keep me")
    saveCoursePromptDraft("Teach a valid course.", sessionOnlyStorage)

    expect(saveCoursePromptDraft("ab", sessionOnlyStorage)).toBe(false)
    expect(readCoursePromptDraft(sessionOnlyStorage)).toBeNull()
    expect(unrelatedPersistentStorage.getItem("unrelated")).toBe("keep me")
  })

  it("fails closed when browser storage is unavailable", () => {
    const unavailableStorage = {
      getItem: () => {
        throw new DOMException("Blocked", "SecurityError")
      },
      removeItem: () => {
        throw new DOMException("Blocked", "SecurityError")
      },
      setItem: () => {
        throw new DOMException("Blocked", "SecurityError")
      },
    } as unknown as Storage

    expect(
      saveCoursePromptDraft("Teach a valid course.", unavailableStorage),
    ).toBe(false)
    expect(readCoursePromptDraft(unavailableStorage)).toBeNull()
    expect(() => clearCoursePromptDraft(unavailableStorage)).not.toThrow()
  })
})
