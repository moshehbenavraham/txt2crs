import { useEffect, useRef, useState } from "react"

import type { ItemPublic } from "@/client"
import { ContentTypeBadge } from "@/components/Items/ContentTypeBadge"
import { ItemActionsMenu } from "@/components/Items/ItemActionsMenu"
import { SourceUrlCell } from "@/components/Items/SourceUrlCell"
import { cn } from "@/lib/utils"

interface LibraryPreviewProps {
  items: ItemPublic[]
  total: number
}

export function LibraryPreview({ items, total }: LibraryPreviewProps) {
  const [highlightId, setHighlightId] = useState<string | null>(null)
  const previousIdsRef = useRef<string[] | null>(null)
  const idsKey = items.map((item) => item.id).join(",")

  // Brief background emphasis when a newly created item lands in the preview.
  // The toast announces the outcome; this only points at the changed row.
  useEffect(() => {
    const currentIds = idsKey ? idsKey.split(",") : []
    const previousIds = previousIdsRef.current
    if (previousIds) {
      const freshId = currentIds.find((id) => !previousIds.includes(id))
      if (freshId) {
        setHighlightId(freshId)
      }
    }
    previousIdsRef.current = currentIds
  }, [idsKey])

  return (
    <div className="flex flex-col gap-2">
      <ul className="flex flex-col divide-y divide-border overflow-hidden rounded-xl border border-border bg-surface-1">
        {items.map((item) => (
          <li
            key={item.id}
            className={cn(
              "flex flex-col gap-2 p-4 sm:grid sm:grid-cols-[minmax(0,1fr)_auto_minmax(0,15rem)_auto] sm:items-center sm:gap-4",
              highlightId === item.id && "row-highlight",
            )}
          >
            <div className="min-w-0">
              <p className="line-clamp-2 font-medium text-foreground">
                {item.title}
              </p>
              {item.description && (
                <p className="line-clamp-1 text-body-sm text-muted-foreground sm:hidden">
                  {item.description}
                </p>
              )}
            </div>
            <ContentTypeBadge contentType={item.content_type} />
            <div className="min-w-0 text-body-sm">
              {item.source_url ? (
                <SourceUrlCell url={item.source_url} />
              ) : (
                <span className="text-muted-foreground">No source</span>
              )}
            </div>
            <div className="flex justify-end sm:justify-end">
              <ItemActionsMenu item={item} />
            </div>
          </li>
        ))}
      </ul>
      <p className="text-body-sm text-muted-foreground">
        Showing {items.length} of {total} {total === 1 ? "item" : "items"} from
        your library listing.
      </p>
    </div>
  )
}
