import { createFileRoute } from "@tanstack/react-router"

import { LandingPage } from "@/components/Landing/LandingPage"
import { buildPageTitle } from "@/lib/branding"

export const Route = createFileRoute("/")({
  component: LandingPage,
  head: () => ({
    meta: [
      {
        title: buildPageTitle("Create a complete learning package"),
      },
      {
        name: "description",
        content:
          "Turn one topic or source into a researched course, review materials, a student assessment, and an instructor answer key.",
      },
    ],
  }),
})
