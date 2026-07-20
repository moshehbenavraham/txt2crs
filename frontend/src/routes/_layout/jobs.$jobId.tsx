import { createFileRoute } from "@tanstack/react-router"

import {
  CourseJobUnavailable,
  CourseProgressPage,
  CourseProgressUnexpectedError,
} from "@/components/CourseProgress/CourseProgressPage"
import { buildPageTitle } from "@/lib/branding"
import { createJobId } from "@/lib/types"

export const Route = createFileRoute("/_layout/jobs/$jobId")({
  component: JobProgressRouteBoundary,
  errorComponent: CourseProgressUnexpectedError,
  head: () => ({
    meta: [{ title: buildPageTitle("Course progress") }],
  }),
})

/**
 * Validate the untrusted route segment before it reaches the generated query.
 * Invalid and missing/foreign identifiers intentionally share recovery copy.
 */
function JobProgressRouteBoundary() {
  const { jobId: routeJobId } = Route.useParams()
  try {
    return <CourseProgressPage jobId={createJobId(routeJobId)} />
  } catch {
    return <CourseJobUnavailable />
  }
}
