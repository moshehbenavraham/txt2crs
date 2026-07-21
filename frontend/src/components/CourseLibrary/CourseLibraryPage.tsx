import { Link } from "@tanstack/react-router"
import {
  ArrowRight,
  BookOpen,
  FilePlus2,
  RefreshCw,
  TriangleAlert,
} from "lucide-react"

import type { JobLibrarySummaryPublic } from "@/client"
import { PageHeader } from "@/components/Common/PageHeader"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { Skeleton } from "@/components/ui/skeleton"
import { Spinner } from "@/components/ui/spinner"
import {
  formatLibraryTimestamp,
  getLibraryInputLabel,
  getLibraryJobPresentation,
} from "./presentation"
import { useCourseLibraryQuery } from "./queries"

const LIBRARY_SKELETON_KEYS = ["first", "second", "third"] as const

function LibraryHeader() {
  return (
    <PageHeader
      eyebrow="Private learning library"
      title="My courses"
      description="Return to every retained course request, from active research through ready publications."
      actions={
        <Button asChild size="lg">
          <Link to="/create">
            <FilePlus2 data-icon="inline-start" />
            Create a course
          </Link>
        </Button>
      }
    />
  )
}

function CourseLibraryLoading() {
  return (
    <div className="flex flex-col gap-(--space-section)" aria-busy="true">
      <LibraryHeader />
      <section aria-label="Loading courses" className="grid gap-4">
        {LIBRARY_SKELETON_KEYS.map((key) => (
          <Card key={key}>
            <CardHeader>
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-8 w-full max-w-xl" />
              <Skeleton className="h-4 w-56" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-4 w-full max-w-lg" />
            </CardContent>
            <CardFooter>
              <Skeleton className="h-10 w-full sm:w-36" />
            </CardFooter>
          </Card>
        ))}
      </section>
    </div>
  )
}

function CourseLibraryError({ retry }: { retry: () => void }) {
  return (
    <div className="flex flex-col gap-(--space-section)">
      <LibraryHeader />
      <Alert variant="destructive">
        <TriangleAlert aria-hidden="true" />
        <AlertTitle>Your course library could not be loaded</AlertTitle>
        <AlertDescription>
          <p>
            Check your connection and try again. Your retained course jobs have
            not been changed.
          </p>
          <Button
            type="button"
            variant="outline"
            className="mt-3 min-h-11"
            onClick={retry}
          >
            <RefreshCw data-icon="inline-start" />
            Try again
          </Button>
        </AlertDescription>
      </Alert>
    </div>
  )
}

function EmptyCourseLibrary() {
  return (
    <Empty className="min-h-80 border bg-surface-1">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <BookOpen aria-hidden="true" />
        </EmptyMedia>
        <EmptyTitle>
          <h2>Your course shelf is ready</h2>
        </EmptyTitle>
        <EmptyDescription>
          Create your first learning package and it will remain discoverable
          here across sessions and devices.
        </EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button asChild size="lg">
          <Link to="/create">
            <FilePlus2 data-icon="inline-start" />
            Create your first course
          </Link>
        </Button>
      </EmptyContent>
    </Empty>
  )
}

function LibraryCourseRow({ job }: { job: JobLibrarySummaryPublic }) {
  const presentation = getLibraryJobPresentation(job)
  const createdAt = formatLibraryTimestamp(job.created_at)
  const updatedAt = formatLibraryTimestamp(job.updated_at)
  const progressDetail =
    job.progress.total_units === null
      ? null
      : `${job.progress.completed_units} of ${job.progress.total_units} accepted stages`

  return (
    <li className="[content-visibility:auto] [contain-intrinsic-size:auto_220px]">
      <Card>
        <CardHeader className="min-w-0 has-data-[slot=card-action]:grid-cols-[minmax(0,1fr)_auto]">
          <CardTitle className="min-w-0">
            <h2 className="min-w-0 [overflow-wrap:anywhere] font-display text-display-sm text-foreground">
              {job.title}
            </h2>
          </CardTitle>
          <CardDescription className="min-w-0">
            Created from {getLibraryInputLabel(job.input_type)} on{" "}
            <time dateTime={job.created_at}>{createdAt}</time>
          </CardDescription>
          <CardAction>
            <Badge variant={presentation.badgeVariant}>
              {presentation.label}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <p className="text-body text-foreground">{presentation.message}</p>
          {progressDetail ? (
            <p className="text-body-sm text-muted-foreground">
              {progressDetail}
            </p>
          ) : null}
        </CardContent>
        <CardFooter className="flex-col items-stretch gap-4 border-t sm:flex-row sm:items-center sm:justify-between">
          <p className="text-body-sm text-muted-foreground">
            Last activity <time dateTime={job.updated_at}>{updatedAt}</time>
          </p>
          <Button
            asChild
            variant="outline"
            className="min-h-11 w-full sm:w-auto"
          >
            <Link to="/jobs/$jobId" params={{ jobId: job.job_id }}>
              {presentation.actionLabel}
              <ArrowRight data-icon="inline-end" />
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </li>
  )
}

export function CourseLibraryPage() {
  const libraryQuery = useCourseLibraryQuery()

  if (libraryQuery.isPending) {
    return <CourseLibraryLoading />
  }
  if (libraryQuery.isError && !libraryQuery.data) {
    return <CourseLibraryError retry={() => void libraryQuery.refetch()} />
  }

  const jobs = libraryQuery.data.pages.flatMap((page) => page.data)
  return (
    <div className="flex flex-col gap-(--space-section)">
      <LibraryHeader />

      {jobs.length === 0 ? (
        <EmptyCourseLibrary />
      ) : (
        <section aria-labelledby="course-library-list" className="grid gap-5">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-caption text-primary">Newest first</p>
              <h2 id="course-library-list" className="text-display-sm">
                Retained course requests
              </h2>
            </div>
            <p className="text-body-sm text-muted-foreground">
              Showing {jobs.length} {jobs.length === 1 ? "course" : "courses"}
            </p>
          </div>

          {libraryQuery.isError ? (
            <Alert variant="warning">
              <TriangleAlert aria-hidden="true" />
              <AlertTitle>Some courses could not be refreshed</AlertTitle>
              <AlertDescription>
                The courses already shown are still available. Try loading the
                page again to refresh the complete library.
              </AlertDescription>
            </Alert>
          ) : null}

          <ol className="grid gap-4">
            {jobs.map((job) => (
              <LibraryCourseRow key={job.job_id} job={job} />
            ))}
          </ol>

          {libraryQuery.hasNextPage ? (
            <div className="flex justify-center pt-2">
              <Button
                type="button"
                variant="secondary"
                size="lg"
                disabled={libraryQuery.isFetchingNextPage}
                onClick={() => void libraryQuery.fetchNextPage()}
              >
                {libraryQuery.isFetchingNextPage ? (
                  <Spinner data-icon="inline-start" />
                ) : null}
                {libraryQuery.isFetchingNextPage
                  ? "Loading older courses"
                  : "Load older courses"}
              </Button>
            </div>
          ) : null}
        </section>
      )}
    </div>
  )
}
