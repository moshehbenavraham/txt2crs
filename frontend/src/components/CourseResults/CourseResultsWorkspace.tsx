import { FileWarning, RefreshCw, X } from "lucide-react"
import { useMemo } from "react"

import type { JobStatusPublic } from "@/client"
import { PublicationCard } from "@/components/CourseResults/PublicationCard"
import {
  buildPublicationPresentations,
  type PublicationPresentation,
} from "@/components/CourseResults/presentation"
import {
  shouldLoadArtifactManifest,
  useArtifactManifestQuery,
} from "@/components/CourseResults/queries"
import { ResultDisclosure } from "@/components/CourseResults/ResultDisclosure"
import { useArtifactTransfer } from "@/components/CourseResults/useArtifactTransfer"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { htmlPreviewMaxBytes } from "@/lib/public-config"
import type { JobId } from "@/lib/types"

interface CourseResultsWorkspaceProps {
  jobId: JobId
  snapshot: JobStatusPublic
}

function ResultsLoading() {
  return (
    <section
      aria-labelledby="learning-package-publications"
      aria-busy="true"
      className="grid gap-6"
    >
      <div className="max-w-xl">
        <p className="text-caption text-primary">Complete collection</p>
        <h2 id="learning-package-publications" className="mt-3 text-display-md">
          Learning package publications
        </h2>
        <p className="mt-3 text-body-sm text-muted-foreground" role="status">
          Preparing the private publication index...
        </p>
      </div>
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {["course", "review", "assessment", "answer"].map((key) => (
          <div key={key} className="grid gap-4 rounded-2xl border p-6">
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-7 w-2/3" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-11 w-full" />
          </div>
        ))}
      </div>
    </section>
  )
}

function ResultsUnavailable({
  isRetrying,
  onRetry,
}: {
  isRetrying: boolean
  onRetry: () => void
}) {
  return (
    <section aria-labelledby="learning-package-publications">
      <h2 id="learning-package-publications" className="sr-only">
        Learning package publications
      </h2>
      <Alert variant="warning">
        <FileWarning aria-hidden="true" />
        <AlertTitle>Publication files are not available</AlertTitle>
        <AlertDescription>
          <p>
            The private file index could not be opened. Check the connection and
            try again.
          </p>
          <Button
            type="button"
            variant="outline"
            className="mt-3 min-h-11"
            disabled={isRetrying}
            onClick={onRetry}
          >
            <RefreshCw data-icon="inline-start" aria-hidden="true" />
            {isRetrying ? "Trying again..." : "Try again"}
          </Button>
        </AlertDescription>
      </Alert>
    </section>
  )
}

function getVerifiedPublications(
  snapshot: JobStatusPublic,
  manifest: Parameters<typeof buildPublicationPresentations>[0],
): PublicationPresentation[] | null {
  try {
    const publications = buildPublicationPresentations(
      manifest,
      htmlPreviewMaxBytes,
    )
    const observedArtifactCount = publications.reduce(
      (count, publication) => count + publication.artifacts.length,
      0,
    )
    return observedArtifactCount === snapshot.artifacts.count
      ? publications
      : null
  } catch {
    return null
  }
}

/** Completed-state composition for private publications and research facts. */
export function CourseResultsWorkspace({
  jobId,
  snapshot,
}: CourseResultsWorkspaceProps) {
  const artifactQuery = useArtifactManifestQuery(jobId, snapshot)
  const transferControls = useArtifactTransfer()
  const publications = useMemo(
    () =>
      artifactQuery.data
        ? getVerifiedPublications(snapshot, artifactQuery.data)
        : null,
    [artifactQuery.data, snapshot],
  )

  if (!shouldLoadArtifactManifest(snapshot)) {
    return (
      <ResultsUnavailable
        isRetrying={false}
        onRetry={() => {
          void artifactQuery.refetch()
        }}
      />
    )
  }
  if (artifactQuery.isPending) {
    return <ResultsLoading />
  }
  if (!artifactQuery.data || publications === null) {
    return (
      <ResultsUnavailable
        isRetrying={artifactQuery.isFetching}
        onRetry={() => {
          void artifactQuery.refetch()
        }}
      />
    )
  }

  return (
    <section
      aria-labelledby="learning-package-publications"
      className="grid gap-(--space-section) border-t border-border-strong pt-(--space-section)"
    >
      <div className="max-w-2xl">
        <p className="text-caption text-primary">Complete collection</p>
        <h2 id="learning-package-publications" className="mt-3 text-display-md">
          Learning package publications
        </h2>
        <p className="mt-3 text-body-sm leading-6 text-muted-foreground">
          Four aligned publications are ready for private preview or download.
          Choose PDF for a finished copy or open Formats for an editable or web
          version.
        </p>
      </div>

      {transferControls.errorMessage ? (
        <Alert variant="warning">
          <FileWarning aria-hidden="true" />
          <AlertTitle>File not prepared</AlertTitle>
          <AlertDescription>
            <div className="flex flex-wrap items-center gap-3">
              <p>{transferControls.errorMessage}</p>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={transferControls.clearError}
              >
                <X data-icon="inline-start" aria-hidden="true" />
                Dismiss
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="grid items-stretch gap-5 md:grid-cols-2 xl:grid-cols-4">
        {publications.map((publication) => (
          <PublicationCard
            key={publication.deliverable}
            jobId={jobId}
            publication={publication}
            transferControls={transferControls}
          />
        ))}
      </div>

      <ResultDisclosure result={snapshot.result} />
    </section>
  )
}
