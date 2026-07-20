import {
  CheckCircle2,
  ExternalLink,
  LibraryBig,
  TriangleAlert,
} from "lucide-react"

import type { JobResultPublic, JobSourcePublic } from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { getSafeExternalSourceUrl } from "./presentation"

function formatRetrievedDate(retrievedAt: string): string {
  const parsedDate = new Date(retrievedAt)
  return Number.isNaN(parsedDate.getTime())
    ? "Retrieval date unavailable"
    : new Intl.DateTimeFormat("en", {
        dateStyle: "medium",
        timeZone: "UTC",
      }).format(parsedDate)
}

function SourceReference({ source }: { source: JobSourcePublic }) {
  const safeUrl = getSafeExternalSourceUrl(source.url)
  return (
    <li className="grid gap-1 border-b border-border py-4 last:border-b-0">
      {safeUrl ? (
        <a
          className="flex min-w-0 max-w-full items-start gap-2 font-medium text-primary underline-offset-4 hover:underline"
          href={safeUrl}
          target="_blank"
          rel="noopener noreferrer"
          referrerPolicy="no-referrer"
        >
          <span className="min-w-0 break-all">{source.title}</span>
          <ExternalLink aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
        </a>
      ) : (
        <span className="break-all font-medium">{source.title}</span>
      )}
      <span className="break-words text-body-sm text-muted-foreground">
        {source.publisher} {"\u00b7"} Retrieved{" "}
        <time dateTime={source.retrieved_at}>
          {formatRetrievedDate(source.retrieved_at)}
        </time>
      </span>
    </li>
  )
}

/** Display-safe bibliography and conflict truth from the completed job. */
export function ResultDisclosure({
  result,
}: {
  result: JobResultPublic | null
}) {
  return (
    <section aria-labelledby="result-research-notes" className="grid gap-6">
      <div className="max-w-2xl">
        <p className="text-caption text-primary">Research record</p>
        <h2 id="result-research-notes" className="mt-3 text-display-md">
          Sources and research notes
        </h2>
        <p className="mt-3 text-body-sm text-muted-foreground">
          Review the display-safe references and any source disagreements
          reported with this completed package.
        </p>
      </div>

      {!result ? (
        <Alert variant="warning">
          <TriangleAlert aria-hidden="true" />
          <AlertTitle>Research summary unavailable</AlertTitle>
          <AlertDescription>
            The publications remain private, but their source summary could not
            be displayed.
          </AlertDescription>
        </Alert>
      ) : (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(16rem,0.85fr)]">
          <div>
            <div className="flex items-center gap-2">
              <LibraryBig
                aria-hidden="true"
                className="size-5 text-muted-foreground"
              />
              <h3>References</h3>
            </div>
            {result.sources.length > 0 ? (
              <ul className="mt-3">
                {result.sources.map((source, sourceIndex) => (
                  <SourceReference
                    key={`${sourceIndex}-${source.title}-${source.publisher}`}
                    source={source}
                  />
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-body-sm text-muted-foreground">
                No display-safe source references were included.
              </p>
            )}
            {result.sources_truncated ? (
              <p className="mt-3 text-body-sm text-muted-foreground">
                Additional source references were omitted from this bounded
                summary.
              </p>
            ) : null}
          </div>

          <div>
            <Separator className="mb-6 lg:hidden" />
            {result.conflicts.length > 0 ? (
              <Alert variant="warning">
                <TriangleAlert aria-hidden="true" />
                <AlertTitle>Source conflicts reported</AlertTitle>
                <AlertDescription>
                  <ul className="grid list-disc gap-2 pl-5">
                    {result.conflicts.map((conflict, conflictIndex) => (
                      <li key={`${conflictIndex}-${conflict}`}>{conflict}</li>
                    ))}
                  </ul>
                  {result.conflicts_truncated ? (
                    <p className="mt-2">
                      Additional conflict notes were omitted from this bounded
                      summary.
                    </p>
                  ) : null}
                </AlertDescription>
              </Alert>
            ) : (
              <div className="flex items-start gap-3">
                <CheckCircle2
                  aria-hidden="true"
                  className="mt-0.5 size-5 shrink-0 text-stage-complete"
                />
                <div>
                  <h3>No source conflicts reported</h3>
                  <p className="mt-2 text-body-sm text-muted-foreground">
                    The completed package did not include a source disagreement
                    note.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
