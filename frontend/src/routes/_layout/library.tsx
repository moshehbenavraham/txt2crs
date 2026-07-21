import { createFileRoute } from "@tanstack/react-router"

import { CourseLibraryPage } from "@/components/CourseLibrary/CourseLibraryPage"
import { buildPageTitle } from "@/lib/branding"

export const Route = createFileRoute("/_layout/library")({
  component: CourseLibraryPage,
  head: () => ({
    meta: [{ title: buildPageTitle("My courses") }],
  }),
})
