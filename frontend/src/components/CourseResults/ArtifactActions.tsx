import { ChevronDown, Download, Eye, FileDown } from "lucide-react"
import { lazy, Suspense, useEffect, useRef } from "react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Spinner } from "@/components/ui/spinner"
import type { JobId } from "@/lib/types"
import { createTemporaryArtifactUrl } from "./artifact-transfer"
import type { PublicationPresentation } from "./presentation"
import type { ArtifactTransferControls } from "./useArtifactTransfer"

const HtmlArtifactPreview = lazy(() => import("./HtmlArtifactPreview"))

interface ArtifactActionsProps {
  jobId: JobId
  publication: PublicationPresentation
  transferControls: ArtifactTransferControls
}

interface ScheduledUrlRelease {
  timerId: number
  release: () => void
}

/** Download and preview actions backed only by generated-client transfers. */
export function ArtifactActions({
  jobId,
  publication,
  transferControls,
}: ArtifactActionsProps) {
  const scheduledUrlReleasesRef = useRef<Set<ScheduledUrlRelease>>(new Set())
  const pdfArtifact =
    publication.artifacts.find(({ format }) => format === "pdf") ?? null

  useEffect(
    () => () => {
      // A route change can win the race with the zero-delay cleanup. Release
      // both the timer and URL here so neither resource outlives the card.
      for (const scheduledRelease of scheduledUrlReleasesRef.current) {
        window.clearTimeout(scheduledRelease.timerId)
        scheduledRelease.release()
      }
      scheduledUrlReleasesRef.current.clear()
    },
    [],
  )

  const downloadArtifact = async (
    artifact: PublicationPresentation["artifacts"][number],
  ) => {
    try {
      const verifiedArtifact = await transferControls.loadArtifact(
        jobId,
        artifact,
      )
      const temporaryUrl = createTemporaryArtifactUrl(verifiedArtifact.blob)
      const downloadAnchor = document.createElement("a")
      downloadAnchor.href = temporaryUrl.url
      downloadAnchor.download = verifiedArtifact.fileName
      downloadAnchor.hidden = true
      document.body.append(downloadAnchor)
      downloadAnchor.click()
      downloadAnchor.remove()

      const scheduledRelease: ScheduledUrlRelease = {
        timerId: 0,
        release: temporaryUrl.release,
      }
      scheduledRelease.timerId = window.setTimeout(() => {
        scheduledRelease.release()
        scheduledUrlReleasesRef.current.delete(scheduledRelease)
      }, 0)
      scheduledUrlReleasesRef.current.add(scheduledRelease)
    } catch {
      // The shared transfer hook owns one bounded, learner-safe error message.
      // Avoid a second toast or raw exception on the same failed action.
    }
  }

  const isPdfLoading =
    pdfArtifact !== null &&
    transferControls.isArtifactLoading(pdfArtifact.artifact_id)

  return (
    <div className="flex w-full flex-wrap items-center gap-2">
      {pdfArtifact ? (
        <Button
          type="button"
          className="min-h-11 flex-1"
          disabled={isPdfLoading}
          onClick={() => {
            void downloadArtifact(pdfArtifact)
          }}
          aria-label={`Download ${publication.title} PDF`}
        >
          {isPdfLoading ? (
            <Spinner data-icon="inline-start" />
          ) : (
            <Download data-icon="inline-start" aria-hidden="true" />
          )}
          {isPdfLoading ? "Preparing PDF..." : "Download PDF"}
        </Button>
      ) : null}

      {publication.htmlPreview ? (
        <Suspense
          fallback={
            <Button
              type="button"
              variant="outline"
              className="min-h-11"
              disabled
            >
              <Spinner data-icon="inline-start" />
              Loading preview...
            </Button>
          }
        >
          <HtmlArtifactPreview
            jobId={jobId}
            publicationTitle={publication.title}
            artifact={publication.htmlPreview}
            transferControls={transferControls}
          />
        </Suspense>
      ) : null}

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            className="min-h-11"
            aria-label={`${publication.title} download formats`}
          >
            <FileDown data-icon="inline-start" aria-hidden="true" />
            Formats
            <ChevronDown data-icon="inline-end" aria-hidden="true" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="min-w-56">
          <DropdownMenuLabel>Download format</DropdownMenuLabel>
          <DropdownMenuGroup>
            {publication.artifacts.map((artifact) => {
              const isLoading = transferControls.isArtifactLoading(
                artifact.artifact_id,
              )
              return (
                <DropdownMenuItem
                  key={artifact.artifact_id}
                  className="min-h-11"
                  disabled={isLoading}
                  onSelect={() => {
                    void downloadArtifact(artifact)
                  }}
                >
                  {isLoading ? (
                    <Spinner aria-hidden="true" />
                  ) : artifact.format === "html" ? (
                    <Eye aria-hidden="true" />
                  ) : (
                    <Download aria-hidden="true" />
                  )}
                  <span className="flex-1">
                    {artifact.formatLabel}{" "}
                    <span className="text-muted-foreground">
                      {artifact.sizeLabel}
                    </span>
                  </span>
                </DropdownMenuItem>
              )
            })}
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
