import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type ContentType = "general" | string | null | undefined

interface ContentTypeBadgeProps {
  contentType: ContentType
}

const CONTENT_TYPE_CONFIG: Record<
  string,
  { label: string; className: string }
> = {
  general: {
    label: "General",
    className:
      "bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/30 dark:text-gray-300 dark:border-gray-800",
  },
}

export function ContentTypeBadge({ contentType }: ContentTypeBadgeProps) {
  if (!contentType) {
    return (
      <Badge variant="secondary" className="text-muted-foreground">
        Manual
      </Badge>
    )
  }

  const config = CONTENT_TYPE_CONFIG[contentType]
  if (!config) {
    return (
      <Badge variant="secondary" className="text-muted-foreground">
        Unknown
      </Badge>
    )
  }

  return (
    <Badge variant="outline" className={cn(config.className)}>
      {config.label}
    </Badge>
  )
}
