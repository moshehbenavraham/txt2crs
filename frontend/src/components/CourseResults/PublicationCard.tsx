import { ChevronDown, FileCheck2, LockKeyhole } from "lucide-react"
import { useState } from "react"

import { ArtifactActions } from "@/components/CourseResults/ArtifactActions"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import type { JobId } from "@/lib/types"
import type { PublicationPresentation } from "./presentation"
import type { ArtifactTransferControls } from "./useArtifactTransfer"

interface PublicationCardProps {
  jobId: JobId
  publication: PublicationPresentation
  transferControls: ArtifactTransferControls
}

function PublicationFiles({
  jobId,
  publication,
  transferControls,
}: PublicationCardProps) {
  return (
    <>
      <CardContent>
        <ul className="grid gap-2" aria-label={`${publication.title} formats`}>
          {publication.artifacts.map((artifact) => (
            <li
              key={artifact.artifact_id}
              className="flex min-w-0 items-center justify-between gap-3 border-b border-border py-2 last:border-b-0"
            >
              <span className="flex min-w-0 items-center gap-2 font-medium">
                <FileCheck2
                  aria-hidden="true"
                  className="size-4 shrink-0 text-muted-foreground"
                />
                {artifact.formatLabel}
              </span>
              <span className="shrink-0 text-body-sm text-muted-foreground">
                {artifact.sizeLabel}
              </span>
            </li>
          ))}
        </ul>
        {publication.htmlPreviewUnavailableReason ? (
          <p className="mt-3 text-body-sm text-muted-foreground">
            {publication.htmlPreviewUnavailableReason}
          </p>
        ) : null}
      </CardContent>
      <CardFooter>
        <ArtifactActions
          jobId={jobId}
          publication={publication}
          transferControls={transferControls}
        />
      </CardFooter>
    </>
  )
}

/** One semantic publication cover with full shadcn Card anatomy. */
export function PublicationCard({
  jobId,
  publication,
  transferControls,
}: PublicationCardProps) {
  const [isAnswerKeyOpen, setIsAnswerKeyOpen] = useState(false)
  const titleId = `publication-${publication.deliverable}-title`
  const cardHeader = (
    <CardHeader>
      <Badge variant="outline">
        {publication.folio} / {publication.eyebrow}
      </Badge>
      <CardTitle>
        <h3 id={titleId}>{publication.title}</h3>
      </CardTitle>
      <CardDescription>
        <span>{publication.description}</span>
        <span className="mt-2 block font-medium text-foreground">
          {publication.artifacts.length.toLocaleString()}{" "}
          {publication.artifacts.length === 1 ? "format" : "formats"} available
        </span>
      </CardDescription>
    </CardHeader>
  )

  if (!publication.isInstructorOnly) {
    return (
      <Card
        role="article"
        aria-labelledby={titleId}
        className="result-folio h-full"
        data-deliverable={publication.deliverable}
      >
        {cardHeader}
        <PublicationFiles
          jobId={jobId}
          publication={publication}
          transferControls={transferControls}
        />
      </Card>
    )
  }

  return (
    <Card
      role="article"
      aria-labelledby={titleId}
      className="result-folio h-full"
      data-deliverable={publication.deliverable}
    >
      {cardHeader}
      <Collapsible open={isAnswerKeyOpen} onOpenChange={setIsAnswerKeyOpen}>
        <CardContent>
          <div className="flex items-start gap-3 rounded-xl bg-surface-2 p-4">
            <LockKeyhole
              aria-hidden="true"
              className="mt-0.5 size-5 shrink-0 text-folio-answer-key"
            />
            <div className="min-w-0">
              <p className="font-medium">For instructors</p>
              <p className="mt-1 text-body-sm text-muted-foreground">
                Keep this publication separate while learners complete the
                assessment.
              </p>
            </div>
          </div>
          <CollapsibleTrigger asChild>
            <Button
              type="button"
              variant="outline"
              className="mt-4 min-h-11 w-full"
            >
              {isAnswerKeyOpen ? "Hide" : "Show"} answer key downloads
              <ChevronDown data-icon="inline-end" aria-hidden="true" />
            </Button>
          </CollapsibleTrigger>
        </CardContent>
        <CollapsibleContent>
          <PublicationFiles
            jobId={jobId}
            publication={publication}
            transferControls={transferControls}
          />
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}
