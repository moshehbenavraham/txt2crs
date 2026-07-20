import { queryOptions, useQuery } from "@tanstack/react-query"

import {
  type ArtifactManifestPublic,
  type JobStatusPublic,
  JobsService,
} from "@/client"
import { ApiError } from "@/lib/api-error"
import type { JobId } from "@/lib/types"

const MAXIMUM_AUTOMATIC_ARTIFACT_RETRIES = 2

export class ArtifactManifestIntegrityError extends Error {
  constructor() {
    super("The publication files could not be verified.")
    this.name = "ArtifactManifestIntegrityError"
  }
}

export const artifactManifestQueryKey = (jobId: string) =>
  ["course-jobs", jobId, "artifacts"] as const

/** Load publications only after durable delivery is explicitly committed. */
export function shouldLoadArtifactManifest(snapshot: JobStatusPublic): boolean {
  return (
    snapshot.status === "completed" &&
    snapshot.artifacts.available &&
    snapshot.artifacts.count > 0 &&
    snapshot.artifacts.manifest_url !== null
  )
}

/** Retry connectivity/server failures, never owner denial or bad metadata. */
export function isTransientArtifactReadError(error: unknown): boolean {
  if (error instanceof ArtifactManifestIntegrityError) {
    return false
  }
  if (error instanceof ApiError) {
    return (
      error.status === 0 ||
      error.status === 408 ||
      error.status === 429 ||
      error.status >= 500
    )
  }
  return error instanceof Error
}

export function getArtifactManifestQueryOptions(
  jobId: string,
  isEnabled: boolean,
) {
  return queryOptions({
    queryKey: artifactManifestQueryKey(jobId),
    queryFn: async ({ signal }): Promise<ArtifactManifestPublic> => {
      const manifest = await JobsService.readJobArtifacts({
        path: { job_id: jobId },
        signal,
      })
      // A cross-job cache or transport mix-up must never become a publication
      // action. Keep the error fixed and free of either opaque identifier.
      if (manifest.job_id !== jobId) {
        throw new ArtifactManifestIntegrityError()
      }
      return manifest
    },
    enabled: isEnabled,
    retry: (failureCount, error) =>
      failureCount < MAXIMUM_AUTOMATIC_ARTIFACT_RETRIES &&
      isTransientArtifactReadError(error),
    refetchInterval: false,
    refetchOnMount: "always",
    refetchOnReconnect: "always",
    refetchOnWindowFocus: false,
  })
}

/** Bind the completed owner job to one non-polling private manifest query. */
export function useArtifactManifestQuery(
  jobId: JobId,
  snapshot: JobStatusPublic,
) {
  return useQuery(
    getArtifactManifestQueryOptions(
      jobId,
      shouldLoadArtifactManifest(snapshot),
    ),
  )
}
