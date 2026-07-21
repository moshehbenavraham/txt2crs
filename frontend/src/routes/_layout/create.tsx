import { createFileRoute } from "@tanstack/react-router"

import { PageHeader } from "@/components/Common/PageHeader"
import { CourseCapacityStrip } from "@/components/CourseCapacity/CourseCapacityStrip"
import { useAdmissionCapacityQuery } from "@/components/CourseCapacity/queries"
import { CourseIntakeForm } from "@/components/CourseIntake/CourseIntakeForm"
import { useCourseSubmission } from "@/hooks/useCourseSubmission"
import { buildPageTitle } from "@/lib/branding"

export const Route = createFileRoute("/_layout/create")({
  component: CreateCourseRoute,
  head: () => ({
    meta: [
      {
        title: buildPageTitle("Create a course"),
      },
    ],
  }),
})

/**
 * Stable route identity for the intake workbench.
 *
 * Keeping the route and form composition separate lets the protected layout
 * own authentication while the intake component owns only learner-editable
 * request state.
 */
function CreateCourseRoute() {
  const courseSubmission = useCourseSubmission()
  const admissionCapacityQuery = useAdmissionCapacityQuery()
  const capacityIsExhausted = admissionCapacityQuery.data?.available_jobs === 0

  return (
    <div className="flex flex-col gap-(--space-section)">
      <PageHeader
        eyebrow="Learning studio"
        title="Create a course"
        description="Bring one source, set the learning intent, and create a private package of aligned learner and instructor materials."
      />

      <CourseCapacityStrip
        capacity={admissionCapacityQuery.data}
        isPending={admissionCapacityQuery.isPending}
        isError={admissionCapacityQuery.isError}
        onRetry={() => void admissionCapacityQuery.refetch()}
      />

      <CourseIntakeForm
        onSubmit={courseSubmission.submitCourse}
        isSubmitting={courseSubmission.isSubmitting}
        submissionErrorMessage={courseSubmission.submissionErrorMessage}
        submissionDisabledReason={
          capacityIsExhausted
            ? "A new course reservation is not available yet. Your draft stays here while the rolling window reopens."
            : null
        }
      />
    </div>
  )
}
