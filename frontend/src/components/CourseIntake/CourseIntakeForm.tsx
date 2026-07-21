import { zodResolver } from "@hookform/resolvers/zod"
import { ArrowRight } from "lucide-react"
import { useEffect, useRef } from "react"
import { useForm } from "react-hook-form"

import { InputModeField } from "@/components/CourseIntake/InputModeField"
import {
  type CourseIntakeFormController,
  LearningIntentFields,
} from "@/components/CourseIntake/LearningIntentFields"
import { SourcePreview } from "@/components/CourseIntake/SourcePreview"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import { consumeCoursePromptDraft } from "@/lib/course-draft"
import {
  type CourseIntakeFormValues,
  type CourseIntakeValues,
  courseIntakeSchema,
  createDefaultCourseIntakeValues,
} from "@/lib/schemas"

type CourseInputMode = CourseIntakeFormValues["inputMode"]

interface TextSourceDefinition {
  label: string
  description: string
  placeholder: string
  maximumLength: number
  multiline: boolean
}

const textSourceDefinitions: Record<
  Exclude<CourseInputMode, "upload">,
  TextSourceDefinition
> = {
  prompt: {
    label: "What should the course teach?",
    description:
      "Give a bounded topic or instruction. Specific goals can be added below.",
    placeholder: "For example, teach the foundations of marine food webs",
    maximumLength: 10_000,
    multiline: true,
  },
  text: {
    label: "Paste the source text",
    description:
      "Use text you are permitted to process. Up to 200,000 characters.",
    placeholder: "Paste the complete source text here",
    maximumLength: 200_000,
    multiline: true,
  },
  url: {
    label: "Source URL",
    description:
      "Use a public HTTPS page without embedded credentials or a fragment.",
    placeholder: "https://example.org/learning-source",
    maximumLength: 2_048,
    multiline: false,
  },
  youtube: {
    label: "YouTube URL",
    description:
      "Use a public HTTPS YouTube link. The server verifies supported routing.",
    placeholder: "https://www.youtube.com/watch?v=...",
    maximumLength: 2_048,
    multiline: false,
  },
}

interface CourseIntakeFormProps {
  isSubmitting?: boolean
  onSubmit?: (values: CourseIntakeValues) => Promise<void> | void
  submissionErrorMessage?: string | null
  submissionDisabledReason?: string | null
}

/**
 * One strict intake form spanning source, teaching intent, and consent.
 *
 * Hidden source controls are unregistered and explicitly cleared during mode
 * changes. This prevents stale private text or file references from entering
 * validation, hashing, previews, or a request for another input mode.
 */
export function CourseIntakeForm({
  isSubmitting = false,
  onSubmit,
  submissionErrorMessage = null,
  submissionDisabledReason = null,
}: CourseIntakeFormProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const form = useForm<CourseIntakeFormValues, unknown, CourseIntakeValues>({
    resolver: zodResolver(courseIntakeSchema),
    defaultValues: createDefaultCourseIntakeValues(),
    mode: "onBlur",
    reValidateMode: "onChange",
    shouldFocusError: true,
  })
  const inputMode = form.watch("inputMode")
  const sourceValue = form.watch("sourceValue") ?? ""
  const sourceFile = form.watch("sourceFile")
  const controlsDisabled = isSubmitting || form.formState.isSubmitting
  const setFormValue = form.setValue

  useEffect(() => {
    // Read after the protected route mounts. In development Strict Mode the
    // effect may run twice; the second pass sees no draft and leaves the first
    // restored value intact.
    const savedPrompt = consumeCoursePromptDraft()
    if (savedPrompt !== null) {
      setFormValue("inputMode", "prompt")
      setFormValue("sourceValue", savedPrompt, {
        shouldDirty: true,
        shouldValidate: true,
      })
    }
  }, [setFormValue])

  const clearFileInputElement = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const resetSelectedSource = () => {
    clearFileInputElement()
    if (inputMode === "upload") {
      form.unregister("sourceValue")
      form.setValue("sourceFile", undefined, { shouldDirty: true })
    } else {
      form.unregister("sourceFile")
      form.setValue("sourceValue", "", { shouldDirty: true })
    }
    form.clearErrors(["sourceValue", "sourceFile"])
  }

  const changeInputMode = (nextInputMode: CourseInputMode) => {
    if (nextInputMode === inputMode) {
      return
    }
    form.unregister(["sourceValue", "sourceFile"])
    clearFileInputElement()
    form.clearErrors(["sourceValue", "sourceFile"])
    form.setValue("inputMode", nextInputMode, {
      shouldDirty: true,
      shouldTouch: true,
    })
    if (nextInputMode === "upload") {
      form.setValue("sourceFile", undefined, { shouldDirty: true })
    } else {
      form.setValue("sourceValue", "", { shouldDirty: true })
    }
  }

  const submitValidIntake = async (values: CourseIntakeValues) => {
    await onSubmit?.(values)
  }

  return (
    <Form {...form}>
      <form
        noValidate
        onSubmit={form.handleSubmit(submitValidIntake)}
        className="grid gap-10"
      >
        <section
          aria-labelledby="source-workbench-title"
          className="border-y border-border-strong bg-workbench px-5 py-8 sm:px-8 sm:py-10"
        >
          <p className="text-caption text-primary">Source workbench</p>
          <h2 id="source-workbench-title" className="sr-only">
            Choose and preview a course source
          </h2>

          <InputModeField
            value={inputMode}
            onValueChange={changeInputMode}
            disabled={controlsDisabled}
          />

          <div className="mt-8 grid min-w-0 gap-8 lg:grid-cols-[minmax(0,1.35fr)_minmax(16rem,0.65fr)]">
            <SourceControl
              form={form}
              inputMode={inputMode}
              disabled={controlsDisabled}
              fileInputRef={fileInputRef}
            />
            <SourcePreview
              inputMode={inputMode}
              sourceValue={sourceValue}
              sourceFile={sourceFile}
              onReset={resetSelectedSource}
            />
          </div>
        </section>

        <LearningIntentFields form={form} disabled={controlsDisabled} />

        <div className="flex flex-col gap-5 border-t border-border-strong pt-8 sm:flex-row sm:items-center sm:justify-between">
          <div className="max-w-xl">
            {submissionDisabledReason ? (
              <p role="status" className="text-body-sm leading-6 text-warning">
                {submissionDisabledReason}
              </p>
            ) : (
              <p className="text-body-sm leading-6 text-muted-foreground">
                The request is validated in this browser and again by the
                server. Generation begins only after the server accepts one
                source.
              </p>
            )}
            {submissionErrorMessage ? (
              <p
                role="alert"
                className="mt-3 text-body-sm leading-6 text-destructive"
              >
                {submissionErrorMessage}
              </p>
            ) : null}
          </div>
          <LoadingButton
            type="submit"
            size="lg"
            loading={controlsDisabled}
            disabled={
              onSubmit === undefined || submissionDisabledReason !== null
            }
            className="min-h-12 w-full shrink-0 sm:w-auto"
          >
            {submissionDisabledReason
              ? "Waiting for capacity"
              : "Create my learning package"}
            <ArrowRight aria-hidden="true" />
          </LoadingButton>
        </div>
      </form>
    </Form>
  )
}

interface SourceControlProps {
  disabled: boolean
  fileInputRef: React.MutableRefObject<HTMLInputElement | null>
  form: CourseIntakeFormController
  inputMode: CourseInputMode
}

function SourceControl({
  disabled,
  fileInputRef,
  form,
  inputMode,
}: SourceControlProps) {
  if (inputMode === "upload") {
    return (
      <FormField
        key="upload-source"
        control={form.control}
        name="sourceFile"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Course source file</FormLabel>
            <FormControl>
              <Input
                ref={(inputElement) => {
                  field.ref(inputElement)
                  fileInputRef.current = inputElement
                }}
                name={field.name}
                type="file"
                accept=".pdf,.docx,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation"
                disabled={disabled}
                onBlur={field.onBlur}
                onChange={(event) => {
                  field.onChange(event.target.files?.[0])
                }}
                className="h-auto min-h-14 py-2"
              />
            </FormControl>
            <FormDescription>
              PDF, DOCX, or PPTX with matching declared type {"\u00b7"} 20 MB
              maximum. Selection does not parse the document.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    )
  }

  const sourceDefinition = textSourceDefinitions[inputMode]
  return (
    <FormField
      key={inputMode}
      control={form.control}
      name="sourceValue"
      render={({ field }) => (
        <FormItem>
          <FormLabel>{sourceDefinition.label}</FormLabel>
          <FormControl>
            {sourceDefinition.multiline ? (
              <Textarea
                {...field}
                disabled={disabled}
                maxLength={sourceDefinition.maximumLength}
                placeholder={sourceDefinition.placeholder}
                className={
                  inputMode === "text" ? "min-h-64" : "min-h-40 sm:min-h-48"
                }
              />
            ) : (
              <Input
                {...field}
                type="url"
                inputMode="url"
                disabled={disabled}
                maxLength={sourceDefinition.maximumLength}
                placeholder={sourceDefinition.placeholder}
              />
            )}
          </FormControl>
          <FormDescription>{sourceDefinition.description}</FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  )
}
