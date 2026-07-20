import { describe, expect, expectTypeOf, it } from "vitest"
import {
  type ArtifactId,
  asArtifactId,
  asIdempotencyKey,
  asJobId,
  createArtifactId,
  createIdempotencyKey,
  createJobId,
  type IdempotencyKey,
  type JobId,
} from "./branded"

describe("course domain identifier brands", () => {
  it("validates finite job and artifact identifiers independently from UUIDs", () => {
    expect(createJobId("job-python_01:result.v1")).toBe(
      "job-python_01:result.v1",
    )
    expect(createArtifactId("artifact-course-html")).toBe(
      "artifact-course-html",
    )

    for (const invalidIdentifier of [
      "",
      "-leading-separator",
      "contains a space",
      "contains/slash",
      "x".repeat(129),
    ]) {
      expect(() => createJobId(invalidIdentifier)).toThrow("Invalid JobId")
      expect(() => createArtifactId(invalidIdentifier)).toThrow(
        "Invalid ArtifactId",
      )
    }
  })

  it("accepts the idempotency grammar without applying identifier first-character rules", () => {
    expect(createIdempotencyKey("-retry:key_01.v2")).toBe("-retry:key_01.v2")
    for (const invalidKey of [
      "",
      "contains a space",
      "contains/slash",
      "x".repeat(129),
    ]) {
      expect(() => createIdempotencyKey(invalidKey)).toThrow(
        "Invalid IdempotencyKey",
      )
    }
  })

  it("keeps trusted generated-response casts explicit and nominally distinct", () => {
    expect(asJobId("trusted-job")).toBe("trusted-job")
    expect(asArtifactId("trusted-artifact")).toBe("trusted-artifact")
    expect(asIdempotencyKey("trusted:key")).toBe("trusted:key")

    expectTypeOf<JobId>().not.toEqualTypeOf<ArtifactId>()
    expectTypeOf<JobId>().not.toEqualTypeOf<IdempotencyKey>()
  })
})
