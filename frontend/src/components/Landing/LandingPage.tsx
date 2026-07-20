import { Link, useNavigate } from "@tanstack/react-router"
import {
  ArrowRight,
  BookOpenText,
  ClipboardCheck,
  FileQuestion,
  KeyRound,
  type LucideIcon,
  SearchCheck,
  ShieldCheck,
  Sparkles,
} from "lucide-react"
import { type FormEvent, useState } from "react"

import { Appearance } from "@/components/Common/Appearance"
import { Footer } from "@/components/Common/Footer"
import { Logo } from "@/components/Common/Logo"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { saveCoursePromptDraft } from "@/lib/course-draft"
import { publicSignupVisible } from "@/lib/public-config"
import { coursePromptField } from "@/lib/schemas"

interface PublicationDefinition {
  index: string
  title: string
  description: string
  icon: LucideIcon
}

const publications: PublicationDefinition[] = [
  {
    index: "01",
    title: "Deep-researched course",
    description:
      "A structured curriculum with objectives, modules, and sources.",
    icon: BookOpenText,
  },
  {
    index: "02",
    title: "Review materials",
    description: "Study guides, key ideas, examples, and practice for recall.",
    icon: ClipboardCheck,
  },
  {
    index: "03",
    title: "Student assessment",
    description: "A complete test aligned to what the course actually teaches.",
    icon: FileQuestion,
  },
  {
    index: "04",
    title: "Instructor answer key",
    description: "Correct responses, explanations, and grading guidance.",
    icon: KeyRound,
  },
]

const processSteps = [
  {
    index: "01",
    title: "Bring one source",
    description:
      "Start with a topic, pasted text, public URL, YouTube link, PDF, DOCX, or PPTX.",
  },
  {
    index: "02",
    title: "Set the learning intent",
    description:
      "Choose the audience, level, goals, and age context that the course must enforce.",
  },
  {
    index: "03",
    title: "Follow durable progress",
    description:
      "Return to the same private job page while research, writing, validation, and publishing complete.",
  },
] as const

/**
 * Public product story with no authenticated query or test-only state.
 *
 * Static definitions live outside render so the route stays inexpensive and
 * the semantic publication order cannot drift between themes or viewports.
 */
export function LandingPage() {
  return (
    <div className="min-h-dvh bg-background text-foreground">
      <header className="border-b border-border/70">
        <div className="mx-auto flex min-h-18 max-w-[var(--width-workspace)] items-center justify-between gap-4 px-(--space-page-inline)">
          <Logo />
          <nav
            aria-label="Public navigation"
            className="flex items-center gap-2"
          >
            <Appearance />
            <Button variant="outline" className="min-h-11" asChild>
              <Link to="/login">Sign in</Link>
            </Button>
          </nav>
        </div>
      </header>

      <main>
        <section
          aria-labelledby="landing-title"
          className="border-b border-border/70"
        >
          <div className="mx-auto grid max-w-[var(--width-workspace)] gap-14 px-(--space-page-inline) py-[var(--space-journey-section)] lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)] lg:items-center lg:gap-20">
            <div className="flex max-w-2xl flex-col items-start">
              <p className="text-caption text-primary">
                A research atelier for learning
              </p>
              <h1
                id="landing-title"
                className="mt-5 max-w-[13ch] text-[clamp(2.65rem,6vw,4.9rem)] font-medium leading-[0.98] tracking-[-0.035em]"
              >
                Turn one source into a complete learning package
              </h1>
              <p className="mt-7 max-w-xl text-[1.0625rem] leading-8 text-muted-foreground sm:text-lg">
                Shape any supported topic or source into a cited course, a
                focused review pack, a student test, and a separate instructor
                answer key.
              </p>
              <CourseTopicHandoff />
              <div className="mt-5 flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
                <Button
                  variant="outline"
                  size="lg"
                  className="min-h-12"
                  asChild
                >
                  <Link to="/login">Sign in to create a course</Link>
                </Button>
                {publicSignupVisible ? (
                  <Button
                    variant="ghost"
                    size="lg"
                    className="min-h-12"
                    asChild
                  >
                    <Link to="/signup">Create an account</Link>
                  </Button>
                ) : null}
              </div>
              <p className="mt-4 max-w-lg text-body-sm text-muted-foreground">
                {publicSignupVisible
                  ? "Account creation is available for this local installation. The server confirms access."
                  : "Access is provisioned by this installation's operator. Sign in with your provided account."}
              </p>
            </div>

            <figure className="relative">
              <figcaption className="sr-only">
                One source becomes four learning publications
              </figcaption>
              <div className="mx-auto max-w-md border border-border-strong bg-workbench p-5 sm:p-6 lg:mr-0">
                <div className="flex items-start gap-4">
                  <span className="flex size-11 shrink-0 items-center justify-center border border-stage-active/35 bg-background text-stage-active">
                    <Sparkles aria-hidden="true" className="size-5" />
                  </span>
                  <div className="min-w-0">
                    <p className="text-caption text-muted-foreground">
                      Your starting point
                    </p>
                    <p className="mt-2 font-display text-xl leading-snug">
                      One bounded topic or source
                    </p>
                    <p className="mt-2 text-body-sm text-muted-foreground">
                      Topic {"\u00b7"} text {"\u00b7"} URL {"\u00b7"} video{" "}
                      {"\u00b7"} document {"\u00b7"} slides
                    </p>
                  </div>
                </div>
              </div>

              <div
                aria-hidden="true"
                className="mx-auto h-10 w-px bg-stage-track"
              />

              <div className="grid gap-px overflow-hidden border border-border-strong bg-border-strong sm:grid-cols-2">
                {publications.map((publication) => {
                  const PublicationIcon = publication.icon
                  return (
                    <article
                      key={publication.index}
                      className="min-w-0 bg-publication p-5 text-publication-foreground sm:min-h-52 sm:p-6"
                    >
                      <div className="flex items-center justify-between gap-4">
                        <span className="font-mono text-xs text-muted-foreground">
                          {publication.index}
                        </span>
                        <PublicationIcon
                          aria-hidden="true"
                          className="size-5 text-stage-complete"
                        />
                      </div>
                      <h2 className="mt-8 text-xl">{publication.title}</h2>
                      <p className="mt-3 text-body-sm text-muted-foreground">
                        {publication.description}
                      </p>
                    </article>
                  )
                })}
              </div>
            </figure>
          </div>
        </section>

        <section
          aria-labelledby="process-title"
          className="mx-auto max-w-[var(--width-workspace)] px-(--space-page-inline) py-[var(--space-journey-section)]"
        >
          <div className="max-w-2xl">
            <p className="text-caption text-muted-foreground">
              A precise workflow
            </p>
            <h2 id="process-title" className="mt-3 text-display-lg">
              From source to teachable structure
            </h2>
            <p className="mt-4 text-muted-foreground">
              The system keeps source intake, research, curriculum writing,
              assessment alignment, and publication as distinct checked stages.
            </p>
          </div>
          <ol className="mt-12 grid border-y border-border-strong lg:grid-cols-3">
            {processSteps.map((step) => (
              <li
                key={step.index}
                className="grid grid-cols-[3rem_1fr] gap-4 border-b border-border py-7 last:border-b-0 lg:block lg:border-r lg:border-b-0 lg:px-7 lg:first:pl-0 lg:last:border-r-0 lg:last:pr-0"
              >
                <span className="font-mono text-xs text-primary">
                  {step.index}
                </span>
                <div className="lg:mt-8">
                  <h3>{step.title}</h3>
                  <p className="mt-3 text-body-sm text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section
          aria-labelledby="trust-title"
          className="border-y border-border-strong bg-workbench"
        >
          <div className="mx-auto grid max-w-[var(--width-workspace)] gap-10 px-(--space-page-inline) py-14 md:grid-cols-[minmax(0,0.72fr)_minmax(0,1.28fr)] md:items-start">
            <div>
              <p className="text-caption text-primary">Before you submit</p>
              <h2 id="trust-title" className="mt-3 text-display-md">
                Clear about AI and access
              </h2>
            </div>
            <div className="grid gap-8 sm:grid-cols-2">
              <div className="flex gap-4">
                <SearchCheck
                  aria-hidden="true"
                  className="mt-1 size-5 shrink-0 text-primary"
                />
                <div>
                  <h3>Research is part of generation</h3>
                  <p className="mt-2 text-body-sm text-muted-foreground">
                    After explicit consent, the source may be processed by
                    configured AI and research services to build the learning
                    package.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <ShieldCheck
                  aria-hidden="true"
                  className="mt-1 size-5 shrink-0 text-primary"
                />
                <div>
                  <h3>Jobs stay account-scoped</h3>
                  <p className="mt-2 text-body-sm text-muted-foreground">
                    Progress and generated files require the signed-in owner.
                    Retention and provider handling follow the configured
                    installation and services.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section
          aria-labelledby="access-title"
          className="mx-auto flex max-w-[var(--width-workspace)] flex-col items-start gap-7 px-(--space-page-inline) py-[var(--space-journey-section)] sm:flex-row sm:items-end sm:justify-between"
        >
          <div className="max-w-xl">
            <p className="text-caption text-muted-foreground">
              Ready when your account is
            </p>
            <h2 id="access-title" className="mt-3 text-display-lg">
              Begin with what you want to teach
            </h2>
          </div>
          <Button size="lg" className="min-h-12 w-full sm:w-auto" asChild>
            <Link to="/login">
              Continue to sign in
              <ArrowRight aria-hidden="true" />
            </Link>
          </Button>
        </section>
      </main>

      <Footer />
    </div>
  )
}

/**
 * Preserve one optional public topic through normal authentication.
 *
 * Only a valid bounded prompt enters tab-scoped session storage. The protected
 * intake consumes it once, so revisiting `/create` cannot resurrect stale
 * learner text.
 */
function CourseTopicHandoff() {
  const navigate = useNavigate()
  const [draftTopic, setDraftTopic] = useState("")
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const saveTopicAndContinue = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const promptResult = coursePromptField.safeParse(draftTopic)
    if (!promptResult.success) {
      setErrorMessage(
        promptResult.error.issues[0]?.message ??
          "Enter a valid bounded course topic.",
      )
      return
    }
    if (!saveCoursePromptDraft(promptResult.data)) {
      setErrorMessage(
        "This browser could not save the topic for sign in. You can still sign in and enter it on the creation page.",
      )
      return
    }

    setErrorMessage(null)
    void navigate({ to: "/login" })
  }

  return (
    <form
      onSubmit={saveTopicAndContinue}
      className="mt-9 w-full border-y border-border-strong bg-workbench p-4 sm:p-5"
    >
      <label htmlFor="public-course-topic" className="text-sm font-medium">
        Draft a course topic
      </label>
      <p
        id="public-course-topic-help"
        className="mt-1 text-xs leading-5 text-muted-foreground"
      >
        Optional handoff: save one bounded topic in this browser tab, then sign
        in to finish the learning intent.
      </p>
      <Textarea
        id="public-course-topic"
        value={draftTopic}
        onChange={(event) => {
          setDraftTopic(event.target.value)
          if (errorMessage !== null) {
            setErrorMessage(null)
          }
        }}
        maxLength={10_000}
        rows={3}
        aria-describedby={
          errorMessage
            ? "public-course-topic-help public-course-topic-error"
            : "public-course-topic-help"
        }
        aria-invalid={errorMessage !== null}
        placeholder="For example, teach tidal ecology from first principles"
        className="mt-3 min-h-24 bg-background"
      />
      {errorMessage ? (
        <p
          id="public-course-topic-error"
          role="alert"
          className="mt-3 text-body-sm text-destructive"
        >
          {errorMessage}
        </p>
      ) : null}
      <Button
        type="submit"
        size="lg"
        className="mt-4 h-auto min-h-12 w-full whitespace-normal py-3 text-center"
      >
        Save topic and continue to sign in
        <ArrowRight aria-hidden="true" />
      </Button>
    </form>
  )
}
