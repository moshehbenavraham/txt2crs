import { Plus, Trash2 } from "lucide-react"
import type { UseFormReturn } from "react-hook-form"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import type { CourseIntakeFormValues, CourseIntakeValues } from "@/lib/schemas"

export type CourseIntakeFormController = UseFormReturn<
  CourseIntakeFormValues,
  unknown,
  CourseIntakeValues
>

const learnerAgeOptions = [
  {
    value: "adult",
    label: "Adult learner",
    description: "The intended learner is 18 or older.",
  },
  {
    value: "minor",
    label: "Learner under 18",
    description: "Use age-aware language and safeguards.",
  },
  {
    value: "not_provided",
    label: "Age not provided",
    description: "Do not infer a learner age.",
  },
] as const

function readErrorMessage(error: unknown): string | null {
  if (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof error.message === "string"
  ) {
    return error.message
  }
  return null
}

interface LearningIntentFieldsProps {
  disabled?: boolean
  form: CourseIntakeFormController
}

/**
 * Learner-controlled curriculum intent.
 *
 * Goal management uses the form's primitive string array directly. Focus is
 * moved after add/remove so keyboard and screen-reader users do not have to
 * rediscover their position in a changing list.
 */
export function LearningIntentFields({
  disabled = false,
  form,
}: LearningIntentFieldsProps) {
  const learningGoals = form.watch("learningGoals")
  const learningGoalsError = readErrorMessage(
    form.formState.errors.learningGoals,
  )

  const addLearningGoal = () => {
    if (learningGoals.length >= 10) {
      return
    }
    const nextGoalIndex = learningGoals.length
    form.setValue("learningGoals", [...learningGoals, ""], {
      shouldDirty: true,
      shouldValidate: false,
    })
    requestAnimationFrame(() => {
      form.setFocus(`learningGoals.${nextGoalIndex}`)
    })
  }

  const removeLearningGoal = (goalIndex: number) => {
    const remainingGoals =
      learningGoals.length === 1
        ? [""]
        : learningGoals.filter((_, index) => index !== goalIndex)
    const nextFocusIndex = Math.max(0, goalIndex - 1)
    form.setValue("learningGoals", remainingGoals, {
      shouldDirty: true,
      shouldValidate: true,
    })
    requestAnimationFrame(() => {
      form.setFocus(`learningGoals.${nextFocusIndex}`)
    })
  }

  return (
    <section
      aria-labelledby="learning-intent-title"
      className="border-t border-border-strong pt-10"
    >
      <div className="grid gap-3">
        <p className="text-caption text-primary">Learning intent</p>
        <h2 id="learning-intent-title" className="text-display-md">
          Set the teaching direction
        </h2>
        <p className="max-w-[var(--width-reading)] text-muted-foreground">
          Add only the context that should shape depth, examples, and
          assessment. Optional fields may stay blank.
        </p>
      </div>

      <div className="mt-8 grid gap-7 md:grid-cols-2">
        <FormField
          control={form.control}
          name="level"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Learning level</FormLabel>
              <Select
                value={field.value}
                onValueChange={field.onChange}
                disabled={disabled}
              >
                <FormControl>
                  <SelectTrigger className="min-h-11 w-full">
                    <SelectValue placeholder="Choose a level" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="auto">Choose automatically</SelectItem>
                  <SelectItem value="beginner">Beginner</SelectItem>
                  <SelectItem value="intermediate">Intermediate</SelectItem>
                  <SelectItem value="advanced">Advanced</SelectItem>
                  <SelectItem value="mixed">Mixed levels</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                Automatic lets the source and goals determine the depth.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="audience"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Audience</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  disabled={disabled}
                  maxLength={500}
                  placeholder="For example, new team leads"
                />
              </FormControl>
              <FormDescription>
                Optional {"\u00b7"} who should find the material relevant.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="priorKnowledge"
          render={({ field }) => (
            <FormItem className="md:col-span-2">
              <FormLabel>Prior knowledge</FormLabel>
              <FormControl>
                <Textarea
                  {...field}
                  disabled={disabled}
                  maxLength={2_000}
                  className="min-h-28"
                  placeholder="What can learners already do or explain?"
                />
              </FormControl>
              <FormDescription>
                Optional {"\u00b7"} helps avoid repeating or skipping essential
                ideas.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <fieldset
        className="mt-9 border-y border-border py-7"
        aria-describedby={
          learningGoalsError ? "learning-goals-error" : "learning-goals-help"
        }
      >
        <legend className="text-lg font-medium">Learning goals</legend>
        <p
          id="learning-goals-help"
          className="mt-2 max-w-[var(--width-reading)] text-body-sm text-muted-foreground"
        >
          Write distinct outcomes the course and assessment must cover.
        </p>

        <div className="mt-5 grid gap-4">
          {learningGoals.map((_, goalIndex) => (
            <FormField
              key={goalIndex}
              control={form.control}
              name={`learningGoals.${goalIndex}`}
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center justify-between gap-3">
                    <FormLabel>Learning goal {goalIndex + 1}</FormLabel>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      disabled={disabled}
                      onClick={() => removeLearningGoal(goalIndex)}
                      className="min-h-11"
                      aria-label={`Remove goal ${goalIndex + 1}`}
                    >
                      <Trash2 aria-hidden="true" />
                      Remove
                    </Button>
                  </div>
                  <FormControl>
                    <Input
                      {...field}
                      disabled={disabled}
                      maxLength={500}
                      placeholder="Use an observable verb, such as explain or compare"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          ))}
        </div>

        {learningGoalsError ? (
          <p
            id="learning-goals-error"
            role="alert"
            className="mt-4 text-body-sm text-destructive"
          >
            {learningGoalsError}
          </p>
        ) : null}

        <div className="mt-5 flex flex-wrap items-center gap-4">
          <Button
            type="button"
            variant="outline"
            disabled={disabled || learningGoals.length >= 10}
            onClick={addLearningGoal}
            className="min-h-11"
          >
            <Plus aria-hidden="true" />
            Add learning goal
          </Button>
          <span
            aria-live="polite"
            className="text-body-sm text-muted-foreground"
          >
            {learningGoals.length} of 10 goals
          </span>
        </div>
      </fieldset>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <FormField
          control={form.control}
          name="learnerAgeGroup"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <fieldset className="grid gap-3">
                  <legend className="text-lg font-medium">
                    Learner age context
                  </legend>
                  <FormDescription>
                    Choose only what is known. The form never asks for a birth
                    date.
                  </FormDescription>
                  <div className="mt-2 grid gap-2">
                    {learnerAgeOptions.map((ageOption) => (
                      <label
                        key={ageOption.value}
                        className="flex min-h-14 cursor-pointer items-start gap-3 border border-border px-4 py-3 has-checked:border-primary has-checked:bg-primary/5"
                      >
                        <input
                          ref={field.ref}
                          type="radio"
                          name={field.name}
                          value={ageOption.value}
                          checked={field.value === ageOption.value}
                          onBlur={field.onBlur}
                          onChange={() => field.onChange(ageOption.value)}
                          disabled={disabled}
                          className="mt-0.5 size-5 shrink-0 accent-primary outline-none focus-visible:ring-3 focus-visible:ring-ring"
                        />
                        <span>
                          <span className="block font-medium">
                            {ageOption.label}
                          </span>
                          <span className="mt-1 block text-xs leading-5 text-muted-foreground">
                            {ageOption.description}
                          </span>
                        </span>
                      </label>
                    ))}
                  </div>
                </fieldset>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="consentToAiProcessing"
          render={({ field }) => (
            <FormItem className="self-start border border-border-strong bg-workbench p-5 sm:p-6">
              <div className="flex items-start gap-3">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={(checked) =>
                      field.onChange(checked === true)
                    }
                    disabled={disabled}
                    className="mt-0.5 size-5"
                  />
                </FormControl>
                <div className="grid gap-2">
                  <FormLabel className="min-h-6 text-base leading-6">
                    Allow AI and research processing
                  </FormLabel>
                  <FormDescription className="leading-6">
                    Required. The source and learning intent may be processed by
                    this installation&apos;s configured AI and research services
                    to create the package.
                  </FormDescription>
                  <FormMessage />
                </div>
              </div>
            </FormItem>
          )}
        />
      </div>
    </section>
  )
}
