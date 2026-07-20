import { useCallback, useEffect, useRef, useState } from "react"

import { type ArtifactMetadataPublic, JobsService } from "@/client"
import type { JobId } from "@/lib/types"
import {
  normalizeArtifactResponse,
  type VerifiedArtifactTransfer,
} from "./artifact-transfer"

type ArtifactDownloadOptions = {
  path: {
    job_id: string
    artifact_id: string
  }
  signal?: AbortSignal
}

export interface ArtifactTransferTransport {
  download: (options: ArtifactDownloadOptions) => Promise<string | Blob | File>
}

interface ArtifactTransferCoordinatorOptions {
  download?: ArtifactTransferTransport["download"]
}

export interface ArtifactTransferCoordinator {
  load: (
    jobId: string,
    artifact: ArtifactMetadataPublic,
  ) => Promise<VerifiedArtifactTransfer>
  isLoading: (artifactId: string) => boolean
  dispose: () => void
}

const generatedArtifactDownload: ArtifactTransferTransport["download"] = (
  options,
) => JobsService.downloadJobArtifact(options)

/**
 * Own generated-client requests independently from React render timing.
 *
 * The Map closes the event-loop gap before React can publish a pending state.
 * Abort controllers make unmount and route-change cleanup explicit.
 */
export function createArtifactTransferCoordinator({
  download = generatedArtifactDownload,
}: ArtifactTransferCoordinatorOptions = {}): ArtifactTransferCoordinator {
  const inFlightTransfers = new Map<
    string,
    {
      artifactId: string
      controller: AbortController
      request: Promise<VerifiedArtifactTransfer>
    }
  >()
  let hasDisposed = false

  const load = (
    jobId: string,
    artifact: ArtifactMetadataPublic,
  ): Promise<VerifiedArtifactTransfer> => {
    if (hasDisposed) {
      return Promise.reject(new Error("Artifact transfer is unavailable."))
    }
    const transferKey = `${jobId}\u0000${artifact.artifact_id}`
    const existingTransfer = inFlightTransfers.get(transferKey)
    if (existingTransfer) {
      return existingTransfer.request
    }

    const controller = new AbortController()
    let responseRequest: Promise<string | Blob | File>
    try {
      responseRequest = download({
        path: {
          job_id: jobId,
          artifact_id: artifact.artifact_id,
        },
        signal: controller.signal,
      })
    } catch (error) {
      return Promise.reject(error)
    }
    const request = responseRequest
      .then((responseBody) => normalizeArtifactResponse(responseBody, artifact))
      .finally(() => {
        const currentTransfer = inFlightTransfers.get(transferKey)
        if (currentTransfer?.request === request) {
          inFlightTransfers.delete(transferKey)
        }
      })

    inFlightTransfers.set(transferKey, {
      artifactId: artifact.artifact_id,
      controller,
      request,
    })
    return request
  }

  return {
    load,
    isLoading: (artifactId) =>
      [...inFlightTransfers.values()].some(
        (transfer) => transfer.artifactId === artifactId,
      ),
    dispose: () => {
      if (hasDisposed) {
        return
      }
      hasDisposed = true
      for (const transfer of inFlightTransfers.values()) {
        transfer.controller.abort()
      }
      inFlightTransfers.clear()
    },
  }
}

export function getArtifactTransferErrorMessage(_error: unknown): string {
  return "This file could not be prepared. Try again."
}

export interface ArtifactTransferControls {
  loadArtifact: (
    jobId: JobId,
    artifact: ArtifactMetadataPublic,
  ) => Promise<VerifiedArtifactTransfer>
  isArtifactLoading: (artifactId: string) => boolean
  errorMessage: string | null
  clearError: () => void
}

/** React state adapter for the single-flight generated-client coordinator. */
export function useArtifactTransfer(): ArtifactTransferControls {
  const coordinatorRef = useRef<ArtifactTransferCoordinator | null>(null)
  if (coordinatorRef.current === null) {
    coordinatorRef.current = createArtifactTransferCoordinator()
  }
  const mountedRef = useRef(true)
  const [loadingArtifactIds, setLoadingArtifactIds] = useState<Set<string>>(
    () => new Set(),
  )
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      coordinatorRef.current?.dispose()
      // React Strict Mode deliberately runs one setup/cleanup rehearsal in
      // development. Replacing the disposed coordinator here gives the second
      // setup a fresh transport while an actual unmount simply leaves the
      // unused replacement for garbage collection.
      coordinatorRef.current = createArtifactTransferCoordinator()
    }
  }, [])

  const loadArtifact = useCallback(
    async (
      jobId: JobId,
      artifact: ArtifactMetadataPublic,
    ): Promise<VerifiedArtifactTransfer> => {
      setErrorMessage(null)
      setLoadingArtifactIds((currentIds) => {
        const nextIds = new Set(currentIds)
        nextIds.add(artifact.artifact_id)
        return nextIds
      })
      try {
        const coordinator = coordinatorRef.current
        if (coordinator === null) {
          throw new Error("Artifact transfer is unavailable.")
        }
        return await coordinator.load(jobId, artifact)
      } catch (error) {
        if (mountedRef.current) {
          setErrorMessage(getArtifactTransferErrorMessage(error))
        }
        throw error
      } finally {
        if (mountedRef.current) {
          setLoadingArtifactIds((currentIds) => {
            const nextIds = new Set(currentIds)
            nextIds.delete(artifact.artifact_id)
            return nextIds
          })
        }
      }
    },
    [],
  )

  return {
    loadArtifact,
    isArtifactLoading: (artifactId: string) =>
      loadingArtifactIds.has(artifactId) ||
      coordinatorRef.current?.isLoading(artifactId) === true,
    errorMessage,
    clearError: () => setErrorMessage(null),
  }
}
