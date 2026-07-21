import { renderToStaticMarkup } from "react-dom/server"
import { describe, expect, it } from "vitest"

import type { JobResultPublic } from "@/client"
import { ResultDisclosure } from "./ResultDisclosure"

describe("completed result research diagnostics", () => {
  it("distinguishes fetched candidates, charged units, and accepted sources", () => {
    const result = {
      title: "A diagnostic course",
      audience: "Adult learners",
      level: "beginner",
      language: "en",
      objective_count: 3,
      module_count: 2,
      sources: [],
      sources_truncated: false,
      conflicts: [],
      conflicts_truncated: false,
      research: {
        fetched_source_count: 12,
        charged_source_units: 12,
        accepted_source_count: 10,
      },
    } satisfies JobResultPublic

    const markup = renderToStaticMarkup(<ResultDisclosure result={result} />)

    expect(markup).toContain("Fetched candidates")
    expect(markup).toContain("Charged source units")
    expect(markup).toContain("Accepted sources")
    expect(markup).toContain(">12<")
    expect(markup).toContain(">10<")
  })
})
