import { createFileRoute, Link } from "@tanstack/react-router"
import {
  BookOpenText,
  ClipboardCheck,
  FileQuestion,
  KeyRound,
  type LucideIcon,
  Settings,
  SlidersHorizontal,
} from "lucide-react"

import { PageHeader } from "@/components/Common/PageHeader"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"
import { buildPageTitle } from "@/lib/branding"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: buildPageTitle("Workspace"),
      },
    ],
  }),
})

interface LearningAsset {
  title: string
  description: string
  icon: LucideIcon
}

const learningAssets: LearningAsset[] = [
  {
    title: "Deep-researched course",
    description:
      "A structured curriculum grounded in reviewed sources and clear learning objectives.",
    icon: BookOpenText,
  },
  {
    title: "Review materials",
    description:
      "A focused study pack that reinforces the course's essential ideas and terminology.",
    icon: ClipboardCheck,
  },
  {
    title: "Student assessment",
    description:
      "A complete test aligned to the course objectives and the evidence taught.",
    icon: FileQuestion,
  },
  {
    title: "Instructor answer key",
    description:
      "A separate answer sheet with correct responses and concise explanations.",
    icon: KeyRound,
  },
]

/**
 * Present only capabilities the current durable backend can actually produce.
 *
 * The retired donor library used API contracts that no longer exist. Keeping
 * this overview static avoids inventing counts or job-list semantics while
 * Phase 04 adds the owner-scoped submission and progress experience.
 */
function Dashboard() {
  const { user: currentUser } = useAuth()
  const firstName =
    currentUser?.full_name?.trim().split(/\s+/)[0] || currentUser?.email

  return (
    <div className="flex flex-col gap-(--space-section)">
      <PageHeader
        eyebrow="Learning studio"
        title="Course workspace"
        description={
          firstName
            ? `Welcome back, ${firstName}. Turn one topic or source into a complete, private learning package.`
            : "Turn one topic or source into a complete, private learning package."
        }
        actions={
          <>
            <Button variant="outline" className="h-11 sm:h-9" asChild>
              <Link to="/settings">
                <Settings aria-hidden="true" className="size-4" />
                Account settings
              </Link>
            </Button>
            {currentUser?.is_superuser ? (
              <Button className="h-11 sm:h-9" asChild>
                <Link to="/setup">
                  <SlidersHorizontal aria-hidden="true" className="size-4" />
                  System setup
                </Link>
              </Button>
            ) : null}
          </>
        }
      />

      <section
        aria-labelledby="learning-assets-title"
        className="flex flex-col gap-5"
      >
        <div className="flex max-w-2xl flex-col gap-2">
          <p className="text-caption text-muted-foreground">Complete output</p>
          <h2
            id="learning-assets-title"
            className="font-display text-display-md text-foreground"
          >
            One input. Four learning assets.
          </h2>
          <p className="text-body text-muted-foreground">
            Each generation keeps the learner materials and instructor answer
            key distinct, private, and ready for review.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {learningAssets.map((asset) => {
            const AssetIcon = asset.icon
            return (
              <Card key={asset.title} className="h-full">
                <CardHeader>
                  <div className="mb-2 flex size-10 items-center justify-center rounded-xl bg-accent/15 text-accent-foreground">
                    <AssetIcon aria-hidden="true" className="size-5" />
                  </div>
                  <CardTitle>
                    <h3 className="text-heading">{asset.title}</h3>
                  </CardTitle>
                  <CardDescription>{asset.description}</CardDescription>
                </CardHeader>
                <CardContent className="mt-auto">
                  <p className="text-body-sm text-muted-foreground">
                    Included in every completed learning package.
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>
    </div>
  )
}
