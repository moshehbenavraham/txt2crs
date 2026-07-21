import { RefreshCw } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import type { ArtifactMetadataPublic } from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import type { JobId } from "@/lib/types"
import { createSecuredPreviewDocument } from "./preview-document"
import type { ArtifactTransferControls } from "./useArtifactTransfer"

interface HtmlArtifactPreviewProps {
  jobId: JobId
  publicationTitle: string
  artifact: ArtifactMetadataPublic
  transferControls: ArtifactTransferControls
}

/**
 * Private HTML preview in a separate, empty-capability browser context.
 *
 * The artifact is never assigned to the parent DOM. A parsed preview-only copy
 * receives its CSP before it is assigned to the sandboxed iframe's ``srcDoc``.
 * Keeping the verified document inline avoids an object-URL navigation path
 * that is not rendered consistently by every supported embedded browser.
 */
export default function HtmlArtifactPreview({
  jobId,
  publicationTitle,
  artifact,
  transferControls,
}: HtmlArtifactPreviewProps) {
  const { loadArtifact } = transferControls
  const [isOpen, setIsOpen] = useState(false)
  const [previewDocument, setPreviewDocument] = useState<string | null>(null)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [retryRevision, setRetryRevision] = useState(0)
  const requestRevisionRef = useRef(0)

  useEffect(
    () => () => {
      requestRevisionRef.current += 1
    },
    [],
  )

  useEffect(() => {
    if (!isOpen) {
      return
    }

    const requestRevision = requestRevisionRef.current + retryRevision + 1
    requestRevisionRef.current = requestRevision
    setPreviewError(null)
    setPreviewDocument(null)

    void loadArtifact(jobId, artifact)
      .then(async (verifiedArtifact) => {
        const rawHtml = await verifiedArtifact.blob.text()
        const securedDocument = createSecuredPreviewDocument(
          rawHtml,
          artifact.size_bytes,
        )
        if (requestRevisionRef.current !== requestRevision || !isOpen) {
          return
        }
        setPreviewDocument(securedDocument)
      })
      .catch(() => {
        if (requestRevisionRef.current === requestRevision) {
          setPreviewError("This preview could not be prepared. Try again.")
        }
      })

    return () => {
      requestRevisionRef.current += 1
    }
  }, [artifact, isOpen, jobId, retryRevision, loadArtifact])

  const handleOpenChange = (nextIsOpen: boolean) => {
    setIsOpen(nextIsOpen)
    if (!nextIsOpen) {
      requestRevisionRef.current += 1
      setPreviewDocument(null)
      setPreviewError(null)
    }
  }

  const dialogTitle = `${publicationTitle} HTML preview`

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button
          type="button"
          variant="outline"
          className="min-h-11"
          aria-label={`Preview ${publicationTitle} HTML`}
        >
          Preview
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[92vh] max-w-6xl overflow-hidden p-4 [&_[data-slot=dialog-close]]:size-11 sm:p-6">
        <DialogHeader>
          <DialogTitle>{dialogTitle}</DialogTitle>
          <DialogDescription>
            A private, read-only preview. Download the original HTML to keep a
            local copy.
          </DialogDescription>
        </DialogHeader>

        {previewError ? (
          <Alert variant="warning">
            <AlertTitle>Preview unavailable</AlertTitle>
            <AlertDescription>
              <p>{previewError}</p>
              <Button
                type="button"
                variant="outline"
                className="mt-3 min-h-11"
                onClick={() => setRetryRevision((revision) => revision + 1)}
              >
                <RefreshCw data-icon="inline-start" aria-hidden="true" />
                Try preview again
              </Button>
            </AlertDescription>
          </Alert>
        ) : previewDocument ? (
          <iframe
            className="result-preview-frame"
            srcDoc={previewDocument}
            sandbox=""
            referrerPolicy="no-referrer"
            title={dialogTitle}
          />
        ) : (
          <div
            className="grid min-h-80 gap-4 rounded-xl bg-preview-canvas p-6"
            role="status"
            aria-label={`Preparing ${publicationTitle} preview`}
          >
            <Skeleton className="h-8 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-44 w-full" />
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
