import { readFileSync } from "node:fs"

import { describe, expect, it } from "vitest"

const nginxConf = readFileSync(
  new URL("../../nginx.conf", import.meta.url),
  "utf8",
)

describe("frontend nginx security headers", () => {
  it("includes baseline browser hardening directives", () => {
    expect(nginxConf).toContain("add_header Content-Security-Policy")
    expect(nginxConf).toContain("add_header X-Content-Type-Options")
    expect(nginxConf).toContain("add_header X-Frame-Options")
    expect(nginxConf).toContain("add_header Referrer-Policy")
    expect(nginxConf).toContain("add_header Permissions-Policy")
  })
})
