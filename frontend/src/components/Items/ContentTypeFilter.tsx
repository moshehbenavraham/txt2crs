import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export type ContentTypeFilterValue = "all" | "general"

interface ContentTypeFilterProps {
  value: ContentTypeFilterValue
  onChange: (value: ContentTypeFilterValue) => void
}

const FILTER_OPTIONS: { value: ContentTypeFilterValue; label: string }[] = [
  { value: "all", label: "All Types" },
  { value: "general", label: "General" },
]

export function ContentTypeFilter({ value, onChange }: ContentTypeFilterProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-full sm:w-[140px]">
        <SelectValue placeholder="Filter by type" />
      </SelectTrigger>
      <SelectContent>
        {FILTER_OPTIONS.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
