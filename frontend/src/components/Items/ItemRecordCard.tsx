import type { ItemPublic } from "@/client"
import { ContentTypeBadge } from "@/components/Items/ContentTypeBadge"
import { ItemActionsMenu } from "@/components/Items/ItemActionsMenu"
import { SourceUrlCell } from "@/components/Items/SourceUrlCell"

/**
 * Mobile record representation of an item. Shares data and actions with the
 * desktop table; the ID lives in the edit dialog rather than the first view.
 */
export function ItemRecordCard({ item }: { item: ItemPublic }) {
  return (
    <article className="flex flex-col gap-2 rounded-xl border border-border bg-surface-1 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 flex-col items-start gap-1.5">
          <h3 className="line-clamp-2 font-medium leading-snug text-foreground">
            {item.title}
          </h3>
          <ContentTypeBadge contentType={item.content_type} />
        </div>
        <div className="-mr-2 -mt-2 shrink-0">
          <ItemActionsMenu item={item} />
        </div>
      </div>
      {item.description && (
        <p className="line-clamp-2 text-body-sm text-muted-foreground">
          {item.description}
        </p>
      )}
      <div className="text-body-sm">
        {item.source_url ? (
          <SourceUrlCell url={item.source_url} />
        ) : (
          <span className="text-muted-foreground">No source</span>
        )}
      </div>
    </article>
  )
}
