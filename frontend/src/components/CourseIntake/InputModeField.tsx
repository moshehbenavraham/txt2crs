import {
  FileText,
  Link2,
  type LucideIcon,
  MessageSquareText,
  TextQuote,
  Video,
} from "lucide-react"

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { CourseIntakeFormValues } from "@/lib/schemas"

type CourseInputMode = CourseIntakeFormValues["inputMode"]

interface InputModeDefinition {
  value: CourseInputMode
  label: string
  shortDescription: string
  icon: LucideIcon
}

const inputModeDefinitions: readonly InputModeDefinition[] = [
  {
    value: "prompt",
    label: "Topic",
    shortDescription: "Describe what to teach",
    icon: MessageSquareText,
  },
  {
    value: "text",
    label: "Pasted text",
    shortDescription: "Use text you provide",
    icon: TextQuote,
  },
  {
    value: "url",
    label: "Website",
    shortDescription: "Use a public HTTPS page",
    icon: Link2,
  },
  {
    value: "youtube",
    label: "YouTube",
    shortDescription: "Use a public video URL",
    icon: Video,
  },
  {
    value: "upload",
    label: "Document",
    shortDescription: "Use PDF, DOCX, or PPTX",
    icon: FileText,
  },
] as const

interface InputModeFieldProps {
  disabled?: boolean
  value: CourseInputMode
  onValueChange: (nextMode: CourseInputMode) => void
}

/**
 * Keyboard-operable source selector.
 *
 * Radix owns arrow-key, Home/End, focus, and selected-state behavior. The
 * parent form owns clearing the previous mode so hidden values cannot leak
 * into a different request.
 */
export function InputModeField({
  disabled = false,
  value,
  onValueChange,
}: InputModeFieldProps) {
  return (
    <div className="grid gap-4">
      <div>
        <h2 className="text-xl">Choose the starting source</h2>
        <p className="mt-2 max-w-[var(--width-reading)] text-body-sm text-muted-foreground">
          Select one format. Changing formats clears the previous source from
          this form.
        </p>
      </div>

      <Tabs
        value={value}
        onValueChange={(nextValue) =>
          onValueChange(nextValue as CourseInputMode)
        }
      >
        <TabsList
          aria-label="Course source format"
          className="grid h-auto w-full grid-cols-2 gap-px rounded-none border border-border-strong bg-border-strong p-0 sm:grid-cols-3 lg:grid-cols-5"
        >
          {inputModeDefinitions.map((modeDefinition) => {
            const ModeIcon = modeDefinition.icon
            return (
              <TabsTrigger
                key={modeDefinition.value}
                value={modeDefinition.value}
                disabled={disabled}
                className="min-h-16 min-w-0 flex-col items-start gap-1 rounded-none bg-workbench px-3 py-3 text-left shadow-none last:col-span-2 data-[state=active]:bg-background data-[state=active]:text-primary sm:min-h-20 sm:px-4 lg:last:col-span-1"
              >
                <span className="flex items-center gap-2">
                  <ModeIcon aria-hidden="true" className="size-4" />
                  <span>{modeDefinition.label}</span>
                </span>
                <span className="hidden whitespace-normal text-xs font-normal leading-snug text-muted-foreground sm:block">
                  {modeDefinition.shortDescription}
                </span>
              </TabsTrigger>
            )
          })}
        </TabsList>
      </Tabs>
    </div>
  )
}
