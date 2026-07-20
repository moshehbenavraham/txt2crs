import { FileCheck2, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import type { CourseIntakeFormValues } from "@/lib/schemas"

type CourseInputMode = CourseIntakeFormValues["inputMode"]

const MAXIMUM_VISIBLE_SOURCE_CHARACTERS = 720

const sourcePreviewTitles: Record<
  Exclude<CourseInputMode, "upload">,
  string
> = {
  prompt: "Topic preview",
  text: "Text preview",
  url: "Website preview",
  youtube: "YouTube preview",
}

function formatFileBytes(byteCount: number): string {
  if (byteCount < 1_024) {
    return `${byteCount.toLocaleString()} bytes`
  }
  if (byteCount < 1_048_576) {
    return `${(byteCount / 1_024).toFixed(1)} KB`
  }
  return `${(byteCount / 1_048_576).toFixed(1)} MB`
}

interface SourcePreviewProps {
  inputMode: CourseInputMode
  sourceFile?: File
  sourceValue: string
  onReset: () => void
}

/**
 * Bounded, metadata-only source preview.
 *
 * Uploaded bytes are never read and no object URL is created. Text is capped
 * before rendering so a valid 200,000-character source cannot make the page
 * unusable while the complete value remains in the form.
 */
export function SourcePreview({
  inputMode,
  sourceFile,
  sourceValue,
  onReset,
}: SourcePreviewProps) {
  const normalizedSourceValue = sourceValue.trim()
  const hasSource =
    inputMode === "upload"
      ? sourceFile !== undefined
      : normalizedSourceValue.length > 0

  return (
    <section
      aria-label="Source preview"
      className="min-w-0 border-t border-border-strong pt-6 lg:border-t-0 lg:border-l lg:pt-0 lg:pl-8"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-caption text-muted-foreground">Local check</p>
          <h3 className="mt-2 text-lg">
            {inputMode === "upload"
              ? "Document preview"
              : sourcePreviewTitles[inputMode]}
          </h3>
        </div>
        {hasSource ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="min-h-11 shrink-0"
            aria-label="Remove selected source"
          >
            <X aria-hidden="true" />
            Clear
          </Button>
        ) : null}
      </div>

      {!hasSource ? (
        <div className="mt-6 border border-dashed border-border-strong bg-background/55 px-5 py-8">
          <p className="text-body-sm text-muted-foreground">
            Your selected source will appear here before submission.
          </p>
        </div>
      ) : inputMode === "upload" && sourceFile ? (
        <div className="mt-6 min-w-0 border-y border-border-strong py-5">
          <FileCheck2 aria-hidden="true" className="size-5 text-primary" />
          <p className="mt-4 break-all font-medium">{sourceFile.name}</p>
          <dl className="mt-4 grid gap-3 text-body-sm">
            <div>
              <dt className="text-muted-foreground">Declared media type</dt>
              <dd className="mt-1 break-all font-mono text-xs">
                {sourceFile.type || "Not declared"}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">File size</dt>
              <dd className="mt-1">{formatFileBytes(sourceFile.size)}</dd>
            </div>
          </dl>
          <p className="mt-5 text-xs leading-5 text-muted-foreground">
            Only file facts are shown locally. Document contents are not parsed
            for this preview.
          </p>
        </div>
      ) : (
        <div className="mt-6 min-w-0 border-y border-border-strong py-5">
          <p
            className={`max-h-64 overflow-auto whitespace-pre-wrap text-body-sm leading-6 ${
              inputMode === "url" || inputMode === "youtube"
                ? "break-all font-mono text-xs"
                : "break-words"
            }`}
          >
            {normalizedSourceValue.slice(0, MAXIMUM_VISIBLE_SOURCE_CHARACTERS)}
          </p>
          {normalizedSourceValue.length > MAXIMUM_VISIBLE_SOURCE_CHARACTERS ? (
            <p className="mt-4 text-xs text-muted-foreground">
              Preview limited to the first{" "}
              {MAXIMUM_VISIBLE_SOURCE_CHARACTERS.toLocaleString()} characters.
            </p>
          ) : null}
        </div>
      )}
    </section>
  )
}
