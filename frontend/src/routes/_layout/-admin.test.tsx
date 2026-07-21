import { renderToStaticMarkup } from "react-dom/server"
import { describe, expect, it } from "vitest"

import { AdminPending, Route } from "./admin"

describe("admin route pending state", () => {
  it("keeps page identity visible while authorization and users load", () => {
    const markup = renderToStaticMarkup(<AdminPending />)

    expect(Route.options.pendingComponent).toBe(AdminPending)
    expect(markup).toContain("Administration")
    expect(markup).toContain("Users")
    expect(markup).toContain("Manage user accounts and permissions.")
    expect(markup).toContain('aria-busy="true"')
  })
})
